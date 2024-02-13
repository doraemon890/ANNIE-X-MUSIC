import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import app
from config import SUPPORT_CHAT

BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])

HOT = " "
SMEXY = " "
LEZBIAN = ""
BIGBALL = " "
LANG = " "
CUTIE = " "
HOT = " "
SMEXY = " "
LEZBIAN = " "
BIGBALL = " "
LANG = " "
CUTIE = " "


@app.on_message(filters.command("horny"))
async def horny(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    HORNY = f"**🔥** {mention} **ɪꜱ** {mm}**% ʜᴏʀɴʏ!**"
    await message.reply_text(HORNY, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)


@app.on_message(filters.command("gay"))
async def gay(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    GAY = f"**🍷** {mention} **ɪꜱ** {mm}**% ɢᴀʏ!**"
    await message.reply_text(GAY, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)


@app.on_message(filters.command("lezbian"))
async def lezbian(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    FEK = f"**💜** {mention} **ɪꜱ** {mm}**% ʟᴇᴢʙɪᴀɴ!**"
    await message.reply_text(FEK, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)


@app.on_message(filters.command("boob"))
async def boob(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    BOOBS = f"**🍒** {mention}**'ꜱ ʙᴏᴏʙꜱ ꜱɪᴢᴇ ɪᴢ** {mm}**!**"
    await message.reply_text(BOOBS, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)


@app.on_message(filters.command("cock"))
async def cock(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    COCK = f"**🍆** {mention}**'ꜱ ᴄᴏᴄᴋ ꜱɪᴢᴇ ɪᴢ** {mm}**ᴄᴍ**"
    await message.reply_text(COCK, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)


@app.on_message(filters.command("cute"))
async def cute(_, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = f"[{user_name}](tg://user?id={user_id})"
    mm = random.randint(1, 100)
    CUTE = f"**🍑** {mention} {mm}**% ᴄᴜᴛᴇ**"
    await message.reply_text(CUTE, reply_markup=BUTTON, disable_web_page_preview=True, quote=True)
