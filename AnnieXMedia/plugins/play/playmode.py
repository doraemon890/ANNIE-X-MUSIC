from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from AnnieXMedia import app
from AnnieXMedia.utils.database import get_playmode, get_playtype, is_nonadmin_chat
from AnnieXMedia.utils.decorators import language
from AnnieXMedia.utils.inline.settings import playmode_users_markup
from config import BANNED_USERS
from AnnieXMedia.utils.errors import capture_err


@app.on_message(filters.command(["playmode" , "mode" ] ,prefixes=["/", "!", "%", ",", ".", "@", "#"]) & filters.group & ~BANNED_USERS)
@language
@capture_err
async def playmode_(client, message: Message, _):
    playmode = await get_playmode(message.chat.id)
    if playmode == "Direct":
        Direct = True
    else:
        Direct = None
    is_non_admin = await is_nonadmin_chat(message.chat.id)
    if not is_non_admin:
        Group = True
    else:
        Group = None
    playty = await get_playtype(message.chat.id)
    if playty == "Everyone":
        Playtype = None
    else:
        Playtype = True
    buttons = playmode_users_markup(_, Direct, Group, Playtype)
    response = await message.reply_text(
        _["play_22"].format(message.chat.title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
