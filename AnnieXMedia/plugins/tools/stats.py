# Authored By Certified Coders © 2025
import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaVideo, Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from AnnieXMedia import app
from AnnieXMedia.core.userbot import assistants
from AnnieXMedia.misc import SUDOERS, mongodb
from AnnieXMedia.plugins import ALL_MODULES
from AnnieXMedia.utils.database import get_served_chats, get_served_users, get_sudoers
from AnnieXMedia.utils.decorators.language import language, languageCB
from AnnieXMedia.utils.inline.stats import (
    build_stats_keyboard,
    build_back_keyboard,
    StatsCallbacks,
)
from config import BANNED_USERS


async def _edit_media_or_reply_with_video(cbq, caption: str, reply_markup):
    media = InputMediaVideo(media=config.STATS_VID_URL, caption=caption)
    try:
        await cbq.edit_message_media(media=media, reply_markup=reply_markup)
    except MessageIdInvalid:
        await cbq.message.reply_video(
            video=config.STATS_VID_URL, caption=caption, reply_markup=reply_markup
        )


@app.on_message(filters.command(["stats", "gstats"]) & ~BANNED_USERS)
@language
async def open_stats(client, message: Message, _):
    is_sudo = message.from_user and (message.from_user.id in SUDOERS)
    keyboard = build_stats_keyboard(_, is_sudo)
    await message.reply_video(
        video=config.STATS_VID_URL,
        caption=_["gstats_2"].format(app.mention),
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex(f"^{StatsCallbacks.BACK}$") & ~BANNED_USERS)
@languageCB
async def handle_back_to_stats(client, callback_query, _):
    is_sudo = callback_query.from_user and (callback_query.from_user.id in SUDOERS)
    keyboard = build_stats_keyboard(_, is_sudo)
    await callback_query.edit_message_text(
        text=_["gstats_2"].format(app.mention), reply_markup=keyboard
    )


@app.on_callback_query(filters.regex(f"^{StatsCallbacks.SHOW_OVERVIEW}$") & ~BANNED_USERS)
@languageCB
async def handle_show_overview(client, callback_query, _):
    await callback_query.answer()
    back_keyboard = build_back_keyboard(_)
    await callback_query.edit_message_text(_["gstats_1"].format(app.mention))
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    caption = _["gstats_3"].format(
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
    await _edit_media_or_reply_with_video(callback_query, caption, back_keyboard)


@app.on_callback_query(filters.regex(f"^{StatsCallbacks.SHOW_BOT_STATS}$") & ~BANNED_USERS)
@languageCB
async def handle_show_bot_stats(client, callback_query, _):
    if callback_query.from_user.id not in SUDOERS:
        return await callback_query.answer(_["gstats_4"], show_alert=True)
    back_keyboard = build_back_keyboard(_)
    try:
        await callback_query.answer()
    except Exception:
        pass
    await callback_query.edit_message_text(_["gstats_1"].format(app.mention))
    physical_cores = psutil.cpu_count(logical=False)
    total_cores = psutil.cpu_count(logical=True)
    ram_total_gb = f"{round(psutil.virtual_memory().total / (1024.0 ** 3))} ɢʙ"
    try:
        freq_current = psutil.cpu_freq().current
        if freq_current >= 1000:
            cpu_freq = f"{round(freq_current / 1000, 2)}ɢʜᴢ"
        else:
            cpu_freq = f"{round(freq_current, 2)}ᴍʜᴢ"
    except Exception:
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"
    disk = psutil.disk_usage("/")
    disk_total = str(disk.total / (1024.0 ** 3))[:4]
    disk_used = str(disk.used / (1024.0 ** 3))[:4]
    disk_free = str(disk.free / (1024.0 ** 3))[:4]
    db_stats = await mongodb.command("dbstats")
    data_size_kb = str(db_stats["dataSize"] / 1024)[:6]
    storage_kb = db_stats["storageSize"] / 1024
    collections = db_stats["collections"]
    objects = db_stats["objects"]
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    caption = _["gstats_5"].format(
        app.mention,
        len(ALL_MODULES),
        platform.system(),
        ram_total_gb,
        physical_cores,
        total_cores,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        pytgver,
        disk_total,
        disk_used,
        disk_free,
        served_chats,
        served_users,
        len(BANNED_USERS),
        len(await get_sudoers()),
        data_size_kb,
        storage_kb,
        collections,
        objects,
    )
    await _edit_media_or_reply_with_video(callback_query, caption, back_keyboard)
