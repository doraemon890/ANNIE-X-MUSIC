import asyncio
import html
from typing import List

from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired, RPCError, UserNotParticipant
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from AnnieXMedia import app
from AnnieXMedia.utils.admin_check import is_admin

chatQueue: set[int] = set()
stopProcess: dict[int, bool] = {}

def _in_group(msg: Message) -> bool:
    return msg.chat and msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)

def _in_channel(msg: Message) -> bool:
    return msg.chat and msg.chat.type == ChatType.CHANNEL

def _mention_html(user) -> str:
    name = html.escape((user.first_name or "User").strip())
    return f'<a href="tg://user?id={user.id}">{name}</a>'

async def _bot_is_admin(chat_id: int) -> bool:
    try:
        me = await app.get_chat_member(chat_id, "self")
        return me.status == ChatMemberStatus.ADMINISTRATOR
    except (UserNotParticipant, RPCError):
        return False

async def scan_deleted_members(chat_id: int) -> List:
    users = []
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user and member.user.is_deleted:
                users.append(member.user)
    except (ChannelInvalid, ChatAdminRequired, UserNotParticipant):
        return []
    return users

async def scan_bots(chat_id: int) -> List:
    bots = []
    try:
        async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BOTS):
            bots.append(member.user)
    except (ChannelInvalid, ChatAdminRequired, UserNotParticipant):
        return []
    return bots

async def get_channel_stats(chat_id: int):
    try:
        chat = await app.get_chat(chat_id)
        members_count = chat.members_count or 0
        return chat, members_count
    except:
        return None, 0

async def safe_edit(msg: Message, text: str, reply_markup=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await msg.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)
            return
        except FloodWait as e:
            if attempt == max_retries - 1:
                break
            await asyncio.sleep(e.value)
        except Exception:
            break

def generate_channel_keyboard(chat_id: int, user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Remove Zombies", callback_data=f"clean_zombies:{chat_id}:{user_id}"),
            InlineKeyboardButton("Remove Bots", callback_data=f"clean_bots:{chat_id}:{user_id}")
        ],
        [
            InlineKeyboardButton("Close", callback_data=f"close_panel:{user_id}")
        ]
    ])

def generate_group_keyboard(chat_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Clean Zombies", callback_data=f"confirm_zombies:{chat_id}")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_zombies")]
    ])

@app.on_message(filters.command(["zombies"]) & (filters.private | filters.group))
async def zombie_handler(_: Client, message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    target_id = None

    if len(args) > 1:
        try:
            target_id = int(args[1])
        except ValueError:
            return await message.reply_text(
                "<i>Invalid ID. Use numeric format like <code>-1001234567890</code></i>",
                parse_mode=enums.ParseMode.HTML
            )

    if target_id:
        return await zombie_channel_scan(_, message, target_id, user_id)

    if not _in_group(message):
        return await message.reply_text(
            "<i>Use this command in a group or with a channel ID.</i>\n\n"
            "<b>Example:</b> <code>/zombies -1002014937805</code>",
            parse_mode=enums.ParseMode.HTML
        )

    await zombie_group_scan(_, message)

async def zombie_channel_scan(_: Client, message: Message, channel_id: int, user_id: int):
    status_msg = await message.reply_text("<i>Checking access...</i>", parse_mode=enums.ParseMode.HTML)

    chat, members_count = await get_channel_stats(channel_id)
    if not chat:
        return await status_msg.edit_text(
            "<i>Access Denied</i>\n\n"
            "<b>Add me first, give full rights, then try again.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    if not await _bot_is_admin(channel_id):
        return await status_msg.edit_text(
            "<i>Access Denied</i>\n\n"
            "<b>I need admin rights with ban permission in the channel.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    zombies = await scan_deleted_members(channel_id)
    bots = await scan_bots(channel_id)

    keyboard = generate_channel_keyboard(channel_id, user_id)

    await status_msg.edit_text(
        f"<b>Access</b>\n"
        f"<b>Channel:</b> {html.escape(chat.title)}\n"
        f"<b>Members:</b> <code>{members_count}</code>\n"
        f"<b>Bots:</b> <code>{len(bots)}</code>\n"
        f"<b>Zombies:</b> <code>{len(zombies)}</code>",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def zombie_group_scan(_: Client, message: Message):
    if not await is_admin(message):
        return await message.reply_text(
            "<i>Only admins can use this.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    if not await _bot_is_admin(message.chat.id):
        return await message.reply_text(
            "<i>I need admin rights to scan.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    zombies = await scan_deleted_members(message.chat.id)
    if not zombies:
        return await message.reply_text(
            "<i>No zombies found.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    total = len(zombies)
    keyboard = generate_group_keyboard(message.chat.id)

    await message.reply_text(
        f"<i>Found <code>{total}</code> zombies.</i>\n\n"
        "Remove them?",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_callback_query(filters.regex(r"^clean_zombies:"))
async def clean_zombies_channel(_: Client, cq: CallbackQuery):
    try:
        _, chat_id_str, user_id_str = cq.data.split(":")
        chat_id = int(chat_id_str)
        user_id = int(user_id_str)
    except:
        return await cq.answer("Invalid data.", show_alert=True)

    if cq.from_user.id != user_id:
        return await cq.answer("This panel is not for you.", show_alert=True)

    if not await _bot_is_admin(chat_id):
        return await cq.answer("I no longer have admin rights.", show_alert=True)

    if chat_id in chatQueue:
        return await cq.answer("Cleanup already in progress.", show_alert=True)

    chatQueue.add(chat_id)
    stopProcess[chat_id] = False

    zombies = await scan_deleted_members(chat_id)
    total = len(zombies)

    if total == 0:
        chatQueue.discard(chat_id)
        return await cq.answer("No zombies to remove.", show_alert=True)

    status = await cq.edit_message_text(
        f"<i>Removing {total} zombies...</i>",
        parse_mode=enums.ParseMode.HTML
    )

    removed = 0
    async def ban_user(uid: int) -> bool:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await app.ban_chat_member(chat_id, uid)
                return True
            except FloodWait as e:
                if attempt == max_retries - 1:
                    return False
                await asyncio.sleep(e.value)
            except:
                return False
        return False

    tasks = [ban_user(u.id) for u in zombies]
    batch_size = 15
    for i in range(0, len(tasks), batch_size):
        if stopProcess.get(chat_id, False):
            break
        results = await asyncio.gather(*tasks[i:i + batch_size], return_exceptions=True)
        removed += sum(1 for r in results if r is True)
        await safe_edit(status, f"<i>Removed {removed}/{total} zombies...</i>")

    chatQueue.discard(chat_id)
    if chat_id in stopProcess:
        del stopProcess[chat_id]

    keyboard = generate_channel_keyboard(chat_id, user_id)
    await safe_edit(
        status,
        f"<b>Zombies cleaned!</b>\n"
        f"<code>{removed}</code> out of <code>{total}</code> removed.",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^clean_bots:"))
async def clean_bots_channel(_: Client, cq: CallbackQuery):
    try:
        _, chat_id_str, user_id_str = cq.data.split(":")
        chat_id = int(chat_id_str)
        user_id = int(user_id_str)
    except:
        return await cq.answer("Invalid data.", show_alert=True)

    if cq.from_user.id != user_id:
        return await cq.answer("This panel is not for you.", show_alert=True)

    if not await _bot_is_admin(chat_id):
        return await cq.answer("I no longer have admin rights.", show_alert=True)

    if chat_id in chatQueue:
        return await cq.answer("Cleanup already in progress.", show_alert=True)

    chatQueue.add(chat_id)
    stopProcess[chat_id] = False

    bots = await scan_bots(chat_id)
    total = len(bots)

    if total == 0:
        chatQueue.discard(chat_id)
        return await cq.answer("No bots to remove.", show_alert=True)

    status = await cq.edit_message_text(
        f"<i>Removing {total} bots...</i>",
        parse_mode=enums.ParseMode.HTML
    )

    removed = 0
    async def ban_user(uid: int) -> bool:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await app.ban_chat_member(chat_id, uid)
                return True
            except FloodWait as e:
                if attempt == max_retries - 1:
                    return False
                await asyncio.sleep(e.value)
            except:
                return False
        return False

    tasks = [ban_user(b.id) for b in bots]
    batch_size = 15
    for i in range(0, len(tasks), batch_size):
        if stopProcess.get(chat_id, False):
            break
        results = await asyncio.gather(*tasks[i:i + batch_size], return_exceptions=True)
        removed += sum(1 for r in results if r is True)
        await safe_edit(status, f"<i>Removed {removed}/{total} bots...</i>")

    chatQueue.discard(chat_id)
    if chat_id in stopProcess:
        del stopProcess[chat_id]

    keyboard = generate_channel_keyboard(chat_id, user_id)
    await safe_edit(
        status,
        f"<b>Bots cleaned!</b>\n"
        f"<code>{removed}</code> out of <code>{total}</code> removed.",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^close_panel:"))
async def close_panel(_: Client, cq: CallbackQuery):
    try:
        _, user_id_str = cq.data.split(":")
        user_id = int(user_id_str)
    except:
        return await cq.answer("Error.", show_alert=True)

    if cq.from_user.id != user_id:
        return await cq.answer("Not your panel.", show_alert=True)

    await cq.message.delete()

@app.on_callback_query(filters.regex(r"^confirm_zombies:"))
async def execute_zombie_cleanup(_: Client, cq: CallbackQuery):
    try:
        chat_id = int(cq.data.split(":")[1])
    except:
        return await cq.answer("Invalid data.", show_alert=True)

    if not await is_admin(cq):
        return await cq.answer("Admins only.", show_alert=True)

    if chat_id in chatQueue:
        return await cq.answer("Already running.", show_alert=True)

    chatQueue.add(chat_id)
    stopProcess[chat_id] = False

    zombies = await scan_deleted_members(chat_id)
    total = len(zombies)

    status = await cq.edit_message_text(f"<i>Starting cleanup...</i>", parse_mode=enums.ParseMode.HTML)
    removed = 0

    async def ban_user(uid):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await app.ban_chat_member(chat_id, uid)
                return True
            except FloodWait as e:
                if attempt == max_retries - 1:
                    return False
                await asyncio.sleep(e.value)
            except:
                return False
        return False

    tasks = [ban_user(u.id) for u in zombies]
    batch_size = 15
    for i in range(0, len(tasks), batch_size):
        if stopProcess.get(chat_id, False):
            break
        results = await asyncio.gather(*tasks[i:i + batch_size], return_exceptions=True)
        removed += sum(1 for r in results if r is True)
        await safe_edit(status, f"<i>Removed {removed}/{total}...</i>")

    chatQueue.discard(chat_id)
    if chat_id in stopProcess:
        del stopProcess[chat_id]

    await safe_edit(status, f"<i>Cleanup complete: <code>{removed}</code> removed.</i>")

@app.on_callback_query(filters.regex(r"^cancel_zombies$"))
async def cancel_zombie_cleanup(_: Client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    stopProcess[chat_id] = True
    await cq.edit_message_text("<i>Cancelled.</i>", parse_mode=enums.ParseMode.HTML)