# Authored By Certified Coders © 2025
import os
import tempfile
import inspect
from uuid import uuid4

from PIL import Image
from pyrogram import raw, filters
from pyrogram.errors import StickersetInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AnnieXMedia import app
from config import BOT_USERNAME


def _cs_kwargs(is_anim: bool, is_vid: bool) -> dict:
    params = inspect.signature(raw.functions.stickers.CreateStickerSet).parameters
    kw = {}
    if is_anim and "animated" in params:
        kw["animated"] = True
    if is_vid and "videos" in params:
        kw["videos"] = True
    return kw


@app.on_message(filters.command(["stickerid", "stid"]) & filters.reply)
async def show_ids(_, message):
    st = message.reply_to_message.sticker
    if not st:
        return await message.reply_text("reply to a sticker")
    await message.reply_text(
        f"sticker id: `{st.file_id}`\n"
        f"unique id: `{st.file_unique_id}`"
    )


@app.on_message(filters.command("stdl") & filters.reply)
async def download_sticker(client, message):
    proc = await message.reply_text("➣ downloading…")
    st = message.reply_to_message.sticker
    with tempfile.TemporaryDirectory() as td:
        path = await message.reply_to_message.download(os.path.join(td, "st"))
        if st.is_animated:
            await proc.edit("➣ sending .tgs…")
            await client.send_document(message.chat.id, path, caption="here's your animated sticker!")
        elif st.is_video:
            await proc.edit("➣ sending video…")
            await client.send_video(message.chat.id, path, supports_streaming=True, caption="here's your video sticker!")
        else:
            await proc.edit("➣ converting to png…")
            img = Image.open(path)
            out = f"{path}.png"
            img.save(out, "PNG")
            await client.send_photo(message.chat.id, out, caption="here's your static image!")
    await proc.delete()


@app.on_message(filters.command("packkang") & filters.reply)
async def pack_clone(client, message):
    proc = await message.reply_text("➣ cloning pack…")
    st = message.reply_to_message.sticker
    try:
        sset = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=st.set_name), hash=0
            )
        )
        title = message.command[1] if len(message.command) > 1 else f"{message.from_user.first_name}'s pack"
        short = f"pack_{uuid4().hex[:8]}_by_{BOT_USERNAME}"
        items = []
        for doc in sset.documents:
            emoji = next((a.alt for a in doc.attributes if isinstance(a, raw.types.DocumentAttributeSticker)), "🤔")
            items.append(
                raw.types.InputStickerSetItem(
                    document=raw.types.InputDocument(
                        id=doc.id, access_hash=doc.access_hash, file_reference=doc.file_reference
                    ),
                    emoji=emoji
                )
            )
        await client.invoke(
            raw.functions.stickers.CreateStickerSet(
                user_id=await client.resolve_peer(message.from_user.id),
                title=title,
                short_name=short,
                stickers=items,
                **_cs_kwargs(st.is_animated, st.is_video)
            )
        )
        await proc.edit(
            f"cloned {len(items)} stickers!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("view pack", url=f"https://t.me/addstickers/{short}")]]),
        )
    except StickersetInvalid:
        await proc.edit("invalid sticker set")
    except Exception as e:
        await proc.edit(f"error: {e}")
