import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import Client, filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaVideo, Message, ChatMemberUpdated
from pytgcalls.__version__ import __version__ as pytgver

import config
from ANNIEMUSIC import app
from ANNIEMUSIC.core.userbot import assistants
from ANNIEMUSIC.misc import SUDOERS, mongodb
from ANNIEMUSIC.plugins import ALL_MODULES
from ANNIEMUSIC.utils.database import get_served_chats, get_served_users, get_sudoers, add_served_chat, remove_served_chat
from ANNIEMUSIC.utils.decorators.language import language, languageCB
from ANNIEMUSIC.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS

@app.on_message(filters.command(["stats", "gstats"]) & filters.group & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, message.from_user.id in SUDOERS)
    await message.reply_video(
        video=config.STATS_VID_URL,
        caption=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )

@app.on_callback_query(filters.regex("stats_back") & filters.group & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    upl = stats_buttons(_, CallbackQuery.from_user.id in SUDOERS)
    await CallbackQuery.edit_message_text(
        text=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )

@app.on_callback_query(filters.regex("TopOverall") & filters.group & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    upl = back_stats_buttons(_)
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_3"].format(
        app.mention,
        len(assistants),
        len(BANNED_USERS),
        served_chats,
        served_users,
        len(ALL_MODULES),
        len(SUDOERS),
        config.AUTO_LEAVING_ASSISTANT,
        config.DURATION_LIMIT_MIN,
    )
    med = InputMediaVideo(media=config.STATS_VID_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_video(
            video=config.STATS_VID_URL, caption=text, reply_markup=upl
        )

@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer(_["gstats_4"], show_alert=True)
    upl = back_stats_buttons(_)
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = f"{round(psutil.virtual_memory().total / (1024.0 ** 3))} GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = f"{round(cpu_freq / 1000, 2)} GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)} MHz"
    except:
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0 ** 3)
    used = hdd.used / (1024.0 ** 3)
    free = hdd.free / (1024.0 ** 3)
    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_5"].format(
        app.mention,
        len(ALL_MODULES),
        platform.system(),
        ram,
        p_core,
        t_core,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        pytgver,
        f"{total:.2f}",
        f"{used:.2f}",
        f"{free:.2f}",
        served_chats,
        served_users,
        len(BANNED_USERS),
        len(await get_sudoers()),
        f"{datasize:.2f}",
        storage,
        call["collections"],
        call["objects"],
    )
    med = InputMediaVideo(media=config.STATS_VID_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_video(
            video=config.STATS_VID_URL, caption=text, reply_markup=upl
        )

@app.on_chat_member_updated()
async def chat_member_update_handler(client: Client, chat_member_updated: ChatMemberUpdated):
    if chat_member_updated.new_chat_member.user.id == client.me.id:
        # Bot was added to a group
        if chat_member_updated.new_chat_member.status in ("member", "administrator"):
            await add_served_chat(chat_member_updated.chat.id)
    elif chat_member_updated.old_chat_member.user.id == client.me.id:
        # Bot was removed from a group
        if chat_member_updated.new_chat_member.status == "left":
            await remove_served_chat(chat_member_updated.chat.id)