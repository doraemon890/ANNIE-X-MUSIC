import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message

from ANNIEMUSIC import app
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.misc import db
from ANNIEMUSIC.utils.database import get_assistant, get_authuser_names, get_cmode
from ANNIEMUSIC.utils.decorators import AdminActual, language
from ANNIEMUSIC.utils.formatters import alpha_to_int, get_readable_time
from config import BANNED_USERS, adminlist, lyrical



rel = {}

# ── /reload, /refresh, /admincache ──
@app.on_message(
    filters.command(["admincache", "reload", "refresh"], prefixes=["/", "!","."])
    & filters.group
    & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        if message.chat.id in rel and rel[message.chat.id] > time.time():
            left = get_readable_time((int(rel[message.chat.id]) - int(time.time())))
            return await message.reply_text(_["reload_1"].format(left))

        adminlist[message.chat.id] = []
        async for user in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            if user.privileges and user.privileges.can_manage_video_chats:
                adminlist[message.chat.id].append(user.user.id)

        authusers = await get_authuser_names(message.chat.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[message.chat.id].append(user_id)

        rel[message.chat.id] = int(time.time()) + 180
        await message.reply_text(_["reload_2"])
    except Exception:
        await message.reply_text(_["reload_3"])


# ── /reboot ──
@app.on_message(filters.command("reboot") & filters.group & ~BANNED_USERS)
@AdminActual
async def restart_bot(client, message: Message, _):
    mystic = await message.reply_text(_["reload_4"].format(app.mention))
    await asyncio.sleep(1)

    try:
        db[message.chat.id] = []
        await JARVIS.force_stop_stream(message.chat.id)
    except:
        pass

    userbot = await get_assistant(message.chat.id)
    try:
        await userbot.resolve_peer(message.chat.username or message.chat.id)
    except:
        pass

    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            got = await app.get_chat(chat_id)
            userbot = await get_assistant(chat_id)
            await userbot.resolve_peer(got.username or chat_id)
            db[chat_id] = []
            await JARVIS.force_stop_stream(chat_id)
        except:
            pass

    await mystic.edit_text(_["reload_5"].format(app.mention))