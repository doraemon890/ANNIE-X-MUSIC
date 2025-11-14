import os
import asyncio
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters, enums
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import TopicClosed, PeerIdInvalid, ChannelPrivate, SlowmodeWait
from AnnieXMedia import app
from AnnieXMedia.mongo.welcomedb import is_on, set_state, bump, cool, auto_on

BG_PATH = "AnnieXMedia/assets/annie/welcome.png"
FALLBACK_PIC = "AnnieXMedia/assets/upic.png"
FONT_PATH = "AnnieXMedia/assets/annie/Arimo.ttf"

BTN_VIEW = "๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏"
BTN_ADD = "๏ ᴋɪᴅɴᴀᴘ ᴍᴇ ๏"

CAPTION_TXT = """
**❅────✦ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ✦────❅
{chat_title}
▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ Nᴀᴍᴇ ✧ {mention}
➻ Iᴅ ✧ `{uid}`
➻ Usᴇʀɴᴀᴍᴇ ✧ @{uname}
➻ Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs ✧ {count}
▰▰▰▰▰▰▰▰▰▰▰▰▰**
**❅─────✧❅✦❅✧─────❅**
"""

JOIN_THRESHOLD = 20
TIME_WINDOW = 10
COOL_MINUTES = 5
WELCOME_LIMIT = 5

last_messages = {}

@lru_cache(maxsize=1)
def cached_bg():
    return Image.open(BG_PATH).convert("RGBA")

@lru_cache(maxsize=2)
def cached_font(size=65):
    return ImageFont.truetype(FONT_PATH, size)

def circle(im, size=(835, 839)):
    im = im.resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *size), fill=255)
    im.putalpha(mask)
    return im

def build_pic(av, fn, uid, un):
    os.makedirs("downloads", exist_ok=True)
    bg = cached_bg().copy()
    avatar = circle(Image.open(av))
    bg.paste(avatar, (1887, 390), avatar)
    d = ImageDraw.Draw(bg)
    f = cached_font()
    d.text((421, 715), fn, fill=(242, 242, 242), font=f)
    d.text((270, 1005), str(uid), fill=(242, 242, 242), font=f)
    d.text((570, 1308), un, fill=(242, 242, 242), font=f)
    path = f"downloads/welcome_{uid}.png"
    bg.save(path)
    return path

async def safe_send(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except:
        return None

@app.on_message(filters.command("welcome") & filters.group)
async def toggle(client, m: Message):
    if len(m.command) != 2:
        return await m.reply_text("**Usage:**\n⦿/welcome [on|off]\n➤ Annie Special Welcome.....")
    u = await client.get_chat_member(m.chat.id, m.from_user.id)
    if u.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await m.reply_text("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ sᴛᴀᴛᴜs!**")
    flag = m.command[1].lower()
    if flag not in ("on", "off"):
        return await m.reply_text("**Usage:**\n⦿/welcome [on|off]\n➤ Annie Special Welcome.....")
    cur = await is_on(m.chat.id)
    if flag == "off" and not cur:
        return await m.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
    if flag == "on" and cur:
        return await m.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
    await set_state(m.chat.id, flag)
    await m.reply_text(f"**{'ᴇɴᴀʙʟᴇᴅ' if flag == 'on' else 'ᴅɪsᴀʙʟᴇᴅ'} ᴡᴇʟᴄᴏᴍᴇ ɪɴ {m.chat.title}**")

@app.on_chat_member_updated(filters.group, group=-3)
async def welcome(client, update: ChatMemberUpdated):
    new = update.new_chat_member
    old = update.old_chat_member
    cid = update.chat.id

    if not new or new.status != enums.ChatMemberStatus.MEMBER:
        return
    if old and old.status == enums.ChatMemberStatus.MEMBER:
        return

    me = await client.get_me()
    try:
        await client.get_chat_member(cid, me.id)
    except:
        return

    if not await is_on(cid):
        if await auto_on(cid):
            await safe_send(client.send_message, cid, "**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ʀᴇ-ᴇɴᴀʙʟᴇᴅ.**")
        else:
            return

    burst = await bump(cid, TIME_WINDOW)
    if burst >= JOIN_THRESHOLD:
        minutes = min(60, COOL_MINUTES + max(0, burst - JOIN_THRESHOLD) * 2)
        await cool(cid, minutes)
        await safe_send(client.send_message, cid, f"**ᴍᴀssɪᴠᴇ ᴊᴏɪɴ ᴅᴇᴛᴇᴄᴛᴇᴅ (x{burst}). ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ғᴏʀ {minutes} ᴍɪɴᴜᴛᴇs.**")
        return

    user = new.user
    file_id = None
    if user.photo and hasattr(user.photo, "big_file_id"):
        file_id = user.photo.big_file_id

    avatar = await safe_send(client.download_media, file_id, file_name=f"downloads/pp_{user.id}.png") if file_id else None
    if not avatar:
        avatar = FALLBACK_PIC

    img = build_pic(avatar, user.first_name, user.id, user.username or "No Username")

    members = await safe_send(client.get_chat_members_count, cid) or "?"

    caption = CAPTION_TXT.format(
        chat_title=update.chat.title,
        mention=user.mention,
        uid=user.id,
        uname=user.username or "No Username",
        count=members
    )

    sent = await safe_send(
        client.send_photo,
        cid,
        img,
        caption=caption,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(BTN_VIEW, url=f"tg://openmessage?user_id={user.id}")],
            [InlineKeyboardButton(BTN_ADD, url=f"https://t.me/{client.username}?startgroup=true")],
        ])
    )

    last_messages.setdefault(cid, []).append(sent)
    if len(last_messages[cid]) > WELCOME_LIMIT:
        old_msg = last_messages[cid].pop(0)
        if old_msg:
            await safe_send(old_msg.delete)

    async def cleanup(path):
        if path and os.path.exists(path) and not os.path.abspath(path).startswith(os.path.abspath("AnnieXMedia/assets")):
            try:
                os.remove(path)
            except:
                pass

    asyncio.create_task(cleanup(avatar))
    asyncio.create_task(cleanup(img))
