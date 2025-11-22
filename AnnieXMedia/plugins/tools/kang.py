# Authored By Certified Coders © 2025
import os
import shutil
import subprocess
import tempfile
import traceback
import inspect
from typing import Tuple

from pyrogram import raw, filters
from pyrogram.errors import (
    StickersetInvalid,
    StickersTooMuch,
    StickerEmojiInvalid,
    PeerIdInvalid,
    FloodWait,
    FileReferenceExpired,
    RPCError,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AnnieXMedia import app
from AnnieXMedia.utils.files import resize_file_to_sticker_size
from config import BOT_USERNAME

BOT = BOT_USERNAME.lstrip("@").lower()


def _cs_kwargs(is_anim: bool, is_vid: bool) -> dict:
    """
    Return only the `animated`/`videos` flags supported by this Pyrogram build.
    """
    params = inspect.signature(raw.functions.stickers.CreateStickerSet).parameters
    kw = {}
    if is_anim and "animated" in params:
        kw["animated"] = True
    if is_vid and "videos" in params:
        kw["videos"] = True
    return kw


def _pack_name(user_id: int, *, animated=False, video=False, index=0) -> str:
    """
    Build a valid short_name:
      user<id>_<type>[ _pack<index> ]_by_<bot>
    """
    parts = [f"user{user_id}"]
    parts.append("animated" if animated else "video" if video else "regular")
    if index:
        parts.append(f"pack{index}")
    parts += ["by", BOT]
    return "_".join(parts)


def _pack_title(username: str, *, animated=False, video=False, index=0) -> str:
    """
    Human‑readable pack title:
      <User>'s Sticker/Animated/Video Pack [<index>]
    """
    kind = "Animated" if animated else "Video" if video else "Sticker"
    suffix = f" {index}" if index else ""
    return f"{username}'s {kind} Pack{suffix}"


def _to_input_doc(doc: raw.base.Document) -> raw.types.InputDocument:
    """
    Convert a raw Document into an InputDocument for sticker‑set calls.
    """
    return raw.types.InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference
    )


async def _prepare_media(message, tmp_dir: str, notify) -> Tuple[str, str, bool, bool]:
    r = message.reply_to_message

    if r.sticker:
        await notify.edit("➣ ᴘʀᴏᴄᴇssɪɴɢ sᴛɪᴄᴋᴇʀ…")
        s = r.sticker
        if s.is_animated:
            return "sticker", await r.download(os.path.join(tmp_dir, "sticker.tgs")), True, False
        if s.is_video:
            return "sticker", await r.download(os.path.join(tmp_dir, "sticker.webm")), False, True
        return "sticker", await r.download(os.path.join(tmp_dir, "sticker.png")), False, False

    if r.photo or (r.document and r.document.mime_type and r.document.mime_type.startswith("image/")):
        await notify.edit("➣ ᴄᴏɴᴠᴇʀᴛɪɴɢ ɪᴍᴀɢᴇ…")
        p = await r.download(os.path.join(tmp_dir, "image"))
        p = await resize_file_to_sticker_size(p)
        return "image", p, False, False

    if (
        r.video or r.animation or
        (r.document and (
            r.document.mime_type in ["video/mp4", "video/x-matroska", "image/gif"] or
            (r.document.file_name and r.document.file_name.endswith(".gif"))
        ))
    ):
        await notify.edit("➣ ᴘʀᴏᴄᴇssɪɴɢ ɢɪꜰ/ᴠɪᴅᴇᴏ…")
        raw_v = await r.download(os.path.join(tmp_dir, "raw.mp4"))
        out_v = os.path.join(tmp_dir, "sticker.webm")
        cmd = [
            "ffmpeg", "-y", "-i", raw_v,
            "-vf", "scale=512:512:flags=lanczos:force_original_aspect_ratio=decrease",
            "-ss", "0", "-t", "3",
            "-c:v", "libvpx-vp9", "-b:v", "500k", "-crf", "30",
            "-an", "-r", "30",
            out_v
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode())
        return "video", out_v, False, True

    raise ValueError("unsupported media type")


@app.on_message(filters.command("kang") & filters.reply)
async def kang(client, message):
    notify = await message.reply_text("➣ ᴘʀᴏᴄᴇssɪɴɢ…")
    tmp_dir = tempfile.mkdtemp()

    try:
        kind, path, is_anim, is_vid = await _prepare_media(message, tmp_dir, notify)
        uid = message.from_user.id
        uname = message.from_user.first_name
        limit = 50 if is_anim or is_vid else 120

        idx = 0
        while True:
            short = _pack_name(uid, animated=is_anim, video=is_vid, index=idx)
            try:
                sset = await client.invoke(
                    raw.functions.messages.GetStickerSet(
                        stickerset=raw.types.InputStickerSetShortName(short_name=short),
                        hash=0
                    )
                )
                if len(sset.documents) >= limit:
                    idx += 1
                    continue
                break
            except StickersetInvalid:
                break

        title = _pack_title(uname, animated=is_anim, video=is_vid, index=idx)

        upload = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(uid),
                media=raw.types.InputMediaUploadedDocument(
                    file=await client.save_file(path),
                    mime_type=(
                        "application/x-tgsticker" if is_anim else
                        "video/webm"         if is_vid  else
                        "image/png"
                    ),
                    attributes=[
                        raw.types.DocumentAttributeFilename(file_name=os.path.basename(path)),
                        raw.types.DocumentAttributeSticker(alt="", stickerset=raw.types.InputStickerSetEmpty(), mask=False)
                    ] + (
                        [raw.types.DocumentAttributeVideo(duration=0, w=512, h=512, round_message=False, supports_streaming=False)]
                        if is_vid else []
                    )
                )
            )
        )
        doc = upload.document

        emoji = message.command[1] if len(message.command) > 1 else "🤔"

        try:
            await client.invoke(
                raw.functions.stickers.AddStickerToSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=short),
                    sticker=raw.types.InputStickerSetItem(document=_to_input_doc(doc), emoji=emoji)
                )
            )
            created = False
        except StickersetInvalid:
            await client.invoke(
                raw.functions.stickers.CreateStickerSet(
                    user_id=await client.resolve_peer(uid),
                    title=title,
                    short_name=short,
                    stickers=[raw.types.InputStickerSetItem(document=_to_input_doc(doc), emoji=emoji)],
                    **_cs_kwargs(is_anim, is_vid)
                )
            )
            created = True
        except StickersTooMuch:
            idx += 1
            short = _pack_name(uid, animated=is_anim, video=is_vid, index=idx)
            title = _pack_title(uname, animated=is_anim, video=is_vid, index=idx)
            await client.invoke(
                raw.functions.stickers.CreateStickerSet(
                    user_id=await client.resolve_peer(uid),
                    title=title,
                    short_name=short,
                    stickers=[raw.types.InputStickerSetItem(document=_to_input_doc(doc), emoji=emoji)],
                    **_cs_kwargs(is_anim, is_vid)
                )
            )
            created = True

        sset = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=short),
                hash=0
            )
        )
        count = len(sset.documents)
        kind_lbl = "ᴀɴɪᴍᴀᴛᴇᴅ" if is_anim else "ᴠɪᴅᴇᴏ" if is_vid else "sᴛᴀᴛɪᴄ"

        await notify.edit(
            f"➣ {'ᴄʀᴇᴀᴛᴇᴅ' if created else 'ᴀᴅᴅᴇᴅ ᴛᴏ'} ʏᴏᴜʀ {kind_lbl} ᴘᴀᴄᴋ!\n"
            f"ᴘᴀᴄᴋ: {title}\n"
            f"ᴄᴏᴜɴᴛ: {count}\n"
            f"ᴇᴍᴏᴊɪ: {emoji}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ᴏᴘᴇɴ ᴘᴀᴄᴋ", url=f"https://t.me/addstickers/{short}")]]
            )
        )

    except FloodWait as e:
        await notify.edit(f"flood wait – retry in {e.x}s")
    except (StickerEmojiInvalid, PeerIdInvalid, FileReferenceExpired, RPCError) as err:
        await notify.edit(f"error: {err}")
    except Exception:
        await notify.edit("unexpected error:\n" + traceback.format_exc())
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
