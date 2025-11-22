# Authored By Certified Coders © 2025
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, UnidentifiedImageError
from pyrogram import errors, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from AnnieXMedia import app
from AnnieXMedia.core.dir import COUPLE_DIR
from AnnieXMedia.mongo.couples_db import get_couple, save_couple


ASSETS = Path("AnnieXMedia/assets")
FALLBACK = ASSETS / "upic.png"
OUT_DIR = Path(COUPLE_DIR)


def today() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def tomorrow() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")


def circular(path: str | Path) -> Image.Image:
    try:
        img = Image.open(path).convert("RGBA").resize((486, 486))
    except (FileNotFoundError, UnidentifiedImageError):
        img = Image.open(FALLBACK).convert("RGBA").resize((486, 486))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + img.size, fill=255)
    img.putalpha(mask)
    return img


async def safe_get_user(uid: int):
    try:
        return await app.get_users(uid)
    except errors.PeerIdInvalid:
        return None


async def safe_photo(uid: int, name: str) -> Path:
    try:
        chat = await app.get_chat(uid)
        if chat.photo and chat.photo.big_file_id:
            path = await app.download_media(chat.photo.big_file_id, file_name=OUT_DIR / name)
            return Path(path) if path else FALLBACK
    except Exception:
        pass
    return FALLBACK


async def generate_image(chat_id: int, uid1: int, uid2: int, date: str) -> str:
    base = Image.open(ASSETS / "annie/couple.png").convert("RGBA")
    p1 = await safe_photo(uid1, "pfp1.png")
    p2 = await safe_photo(uid2, "pfp2.png")

    a1 = circular(p1)
    a2 = circular(p2)
    base.paste(a1, (410, 500), a1)
    base.paste(a2, (1395, 500), a2)

    out_path = OUT_DIR / f"couple_{chat_id}_{date.replace('/','-')}.png"
    base.save(out_path)

    for pf in (p1, p2):
        try:
            if pf != FALLBACK and pf.exists() and pf.parent == OUT_DIR:
                pf.unlink()
        except Exception:
            pass

    return str(out_path)


@app.on_message(filters.command("couple"))
async def couples_handler(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.**")

    wait = await message.reply("🦋")
    cid = message.chat.id
    date = today()

    record = await get_couple(cid, date)
    if record:
        uid1, uid2, img_path = record["user1"], record["user2"], record["img"]
        user1 = await safe_get_user(uid1)
        user2 = await safe_get_user(uid2)

        if not (user1 and user2) or not img_path or not Path(img_path).exists():
            record = None

    if not record:
        members = [
            m.user.id async for m in app.get_chat_members(cid, limit=250)
            if not m.user.is_bot
        ]
        if len(members) < 2:
            await wait.edit("**ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.**")
            return

        tries = 0
        while tries < 5:
            uid1, uid2 = random.sample(members, 2)
            user1 = await safe_get_user(uid1)
            user2 = await safe_get_user(uid2)
            if user1 and user2:
                break
            tries += 1
        else:
            await wait.edit("**ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰɪɴᴅ ᴠᴀʟɪᴅ ᴍᴇᴍʙᴇʀꜱ.**")
            return

        img_path = await generate_image(cid, uid1, uid2, date)
        await save_couple(cid, date, {"user1": uid1, "user2": uid2}, img_path)

    caption = (
        "💌 **ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ!** 💗\n\n"
        "╔═══✿═══❀═══✿═══╗\n"
        f"💌 **ᴛᴏᴅᴀʏ'ꜱ ᴄᴏᴜᴘʟᴇ:**\n⤷ {user1.mention} 💞 {user2.mention}\n"
        "╚═══✿═══❀═══✿═══╝\n\n"
        f"📅 **ɴᴇxᴛ ꜱᴇʟᴇᴄᴛɪᴏɴ:** `{tomorrow()}`\n\n"
        "💗 **ᴛᴀɢ ʏᴏᴜʀ ᴄʀᴜꜱʜ — ʏᴏᴜ ᴍɪɢʜᴛ ʙᴇ ɴᴇxᴛ!** 😉"
    )

    await message.reply_photo(img_path, caption=caption)
    await wait.delete()
