"""
-------------------------------------------------------------------------
Single-user moderation commands with complete edge-case handling.

• /ban     – ban a user
• /unban   – unban a user
• /mute    – mute a user
• /unmute  – unmute a user
• /tmute   – temporary mute (e.g., /tmute @user 1h)
• /kick    – kick a user (auto-unban after 2s)
• /dban    – delete message & ban (reply only)
• /sban    – silent ban (no notification)
• /kickme  – user self-kick (auto-unban after 3s)
• /tban    – temporary ban (e.g., /tban @user 1d)

All commands accept reply, @username, or user-ID.
Usage hints, duplicate-state checks, and safe RPC handling throughout.
-------------------------------------------------------------------------
"""

import asyncio
import datetime as dt
from typing import Optional

from pyrogram import filters, enums
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, UserNotParticipant, RPCError
from pyrogram.types import Message, ChatPermissions

from AnnieXMedia import app
from AnnieXMedia.utils.decorator import admin_required
from AnnieXMedia.utils.permissions import extract_user_and_reason, mention, parse_time

# ────────────────────────────────────────────────────────────
# Constants & Helpers
# ────────────────────────────────────────────────────────────
_DEF_MUTE_PERMS = ChatPermissions()

_USAGES = {
    "ban":    "/ban @user [reason] — or reply with /ban [reason]",
    "unban":  "/unban @user [reason] — or reply with /unban [reason]",
    "mute":   "/mute @user [reason] — or reply with /mute [reason]",
    "unmute": "/unmute @user [reason] — or reply with /unmute [reason]",
    "tmute":  "/tmute @user <time> [reason] — or reply with /tmute <time> [reason]",
    "kick":   "/kick @user [reason] — or reply with /kick [reason]",
    "dban":   "Reply to a user's message with /dban [reason]",
    "sban":   "/sban @user — or reply with /sban",
    "tban":   "/tban @user <time> [reason] — or reply with /tban <time> [reason]",
    "kickme": "/kickme — kick yourself from the group",
}

def _usage(cmd: str) -> str:
    return _USAGES.get(cmd, "Invalid usage.")

def _format_success(action: str, msg: Message, uid: int, name: str, reason: Optional[str]) -> str:
    chat = msg.chat.title
    user_m  = mention(uid, name)
    admin_m = mention(msg.from_user.id, msg.from_user.first_name)
    text = (
        f"» {action} ᴀ ᴜsᴇʀ ɪɴ {chat}\n"
        f" ᴜsᴇʀ  : {user_m}\n"
        f" ᴀᴅᴍɪɴ : {admin_m}"
    )
    if reason:
        text += f"\nReason: {reason}"
    return text

async def _get_member_safe(client, chat_id: int, user_id: int):
    try:
        return await client.get_chat_member(chat_id, user_id)
    except (UserNotParticipant, RPCError):
        return None

async def _get_bot_member(client, chat_id: int):
    me = await client.get_me()
    return await _get_member_safe(client, chat_id, me.id)

def _is_admin_status(status: enums.ChatMemberStatus) -> bool:
    return status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)

# ────────────────────────────────────────────────────────────
# /ban
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("ban"))
@admin_required("can_restrict_members")
async def ban_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("ban"))

    uid, name, reason = await extract_user_and_reason(message, client)
    if not uid:
        return

    target = await _get_member_safe(client, message.chat.id, uid)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot ban an admin or the group owner.")

    if target and target.status == enums.ChatMemberStatus.BANNED:
        return await message.reply_text("User is already banned.")

    try:
        await client.ban_chat_member(message.chat.id, uid)
        await message.reply_text(_format_success("Ban", message, uid, name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")

# ────────────────────────────────────────────────────────────
# /unban
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("unban"))
@admin_required("can_restrict_members")
async def unban_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("unban"))

    uid, name, reason = await extract_user_and_reason(message, client)
    if not uid:
        return
    mem = await _get_member_safe(client, message.chat.id, uid)
    if not mem or mem.status != enums.ChatMemberStatus.BANNED:
        return await message.reply_text("User is not banned.")

    try:
        await client.unban_chat_member(message.chat.id, uid)
        await message.reply_text(_format_success("Unban", message, uid, name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need unban permissions.")

# ────────────────────────────────────────────────────────────
# /mute
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("mute"))
@admin_required("can_restrict_members")
async def mute_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("mute"))

    uid, name, reason = await extract_user_and_reason(message, client)
    if not uid:
        return

    target = await _get_member_safe(client, message.chat.id, uid)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot mute an admin or the group owner.")

    if target and target.status == enums.ChatMemberStatus.RESTRICTED and target.permissions == _DEF_MUTE_PERMS:
        return await message.reply_text("User is already muted.")

    try:
        await client.restrict_chat_member(message.chat.id, uid, _DEF_MUTE_PERMS)
        await message.reply_text(_format_success("Mute", message, uid, name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need mute permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")

# ────────────────────────────────────────────────────────────
# /unmute
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("unmute"))
@admin_required("can_restrict_members")
async def unmute_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("unmute"))

    uid, name, reason = await extract_user_and_reason(message, client)
    if not uid:
        return
    mem = await _get_member_safe(client, message.chat.id, uid)
    if not mem or mem.status != enums.ChatMemberStatus.RESTRICTED:
        return await message.reply_text("User is not muted.")

    perms = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    )
    try:
        await client.restrict_chat_member(message.chat.id, uid, perms)
        await message.reply_text(_format_success("Unmute", message, uid, name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need unmute permissions.")

# ────────────────────────────────────────────────────────────
# /tmute
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("tmute"))
@admin_required("can_restrict_members")
async def tmute_cmd(client, message: Message):
    if ((not message.reply_to_message and len(message.command) < 3) or
        (message.reply_to_message and len(message.command) < 2)):
        return await message.reply_text(_usage("tmute"))

    if message.reply_to_message:
        user    = message.reply_to_message.from_user
        time_arg= message.command[1]
        reason  = message.text.partition(time_arg)[2].strip()
    else:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.reply_text("I can’t find that user.")
        time_arg= message.command[2]
        reason  = message.text.partition(time_arg)[2].strip()

    target = await _get_member_safe(client, message.chat.id, user.id)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot mute an admin or the group owner.")

    delta = parse_time(time_arg)
    if not delta:
        return await message.reply_text("Invalid time format. Use s/m/h/d suffix.")

    until = dt.datetime.now(dt.timezone.utc) + delta
    try:
        await client.restrict_chat_member(message.chat.id, user.id, _DEF_MUTE_PERMS, until_date=until)
        await message.reply_text(_format_success(f"Mute for {time_arg}", message, user.id, user.first_name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need mute permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")

# ────────────────────────────────────────────────────────────
# /kick
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("kick"))
@admin_required("can_restrict_members")
async def kick_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("kick"))

    uid, name, reason = await extract_user_and_reason(message, client)
    if not uid:
        return

    target = await _get_member_safe(client, message.chat.id, uid)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot kick an admin or the group owner.")

    try:
        await client.ban_chat_member(message.chat.id, uid)
        await asyncio.sleep(2)
        await client.unban_chat_member(message.chat.id, uid)
        await message.reply_text(_format_success("Kick", message, uid, name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")

# ────────────────────────────────────────────────────────────
# /dban
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("dban"))
@admin_required("can_restrict_members", "can_delete_messages")
async def dban_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(_usage("dban"))

    user   = message.reply_to_message.from_user
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else None

    target = await _get_member_safe(client, message.chat.id, user.id)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot ban an admin or the group owner.")

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.reply_to_message.delete()
        await message.reply_text(_format_success("Ban", message, user.id, user.first_name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need ban & delete permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")

# ────────────────────────────────────────────────────────────
# /sban
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("sban"))
@admin_required("can_restrict_members")
async def sban_cmd(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await message.reply_text(_usage("sban"))

    uid, _, _ = await extract_user_and_reason(message, client)
    if not uid:
        return

    target = await _get_member_safe(client, message.chat.id, uid)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot ban an admin or the group owner.")

    try:
        await client.ban_chat_member(message.chat.id, uid)
        await message.delete()  # silent
    except ChatAdminRequired:
        await message.reply_text("I need ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")

# ────────────────────────────────────────────────────────────
# /kickme
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("kickme"))
async def kickme_cmd(client, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return

    target = await _get_member_safe(client, message.chat.id, message.from_user.id)
    if target and _is_admin_status(target.status):
        return await message.reply_text("Nice try, boss 😅 I can’t kick admins or the owner.")

    bot_mem = await _get_bot_member(client, message.chat.id)
    if not bot_mem or not getattr(bot_mem, "can_restrict_members", False):
        return await message.reply_text("I need ban permissions to kick you. Ask an admin to enable it.")

    try:
        await client.ban_chat_member(message.chat.id, message.from_user.id)
        await asyncio.sleep(3)
        await client.unban_chat_member(message.chat.id, message.from_user.id)
        await message.reply_text("Kicked so hard, your ancestors felt it. 👟💥")
    except ChatAdminRequired:
        await message.reply_text("I need ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I can’t kick admins or the owner.")

# ────────────────────────────────────────────────────────────
# /tban
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("tban"))
@admin_required("can_restrict_members")
async def tban_cmd(client, message: Message):
    if ((not message.reply_to_message and len(message.command) < 3) or
        (message.reply_to_message and len(message.command) < 2)):
        return await message.reply_text(_usage("tban"))

    if message.reply_to_message:
        user    = message.reply_to_message.from_user
        time_arg= message.command[1]
        reason  = message.text.partition(time_arg)[2].strip()
    else:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.reply_text("I can’t find that user.")
        time_arg= message.command[2]
        reason  = message.text.partition(time_arg)[2].strip()

    target = await _get_member_safe(client, message.chat.id, user.id)
    if target and _is_admin_status(target.status):
        return await message.reply_text("I cannot ban an admin or the group owner.")

    delta = parse_time(time_arg)
    if not delta:
        return await message.reply_text("Invalid time format. Use s/m/h/d suffix.")

    until = dt.datetime.now(dt.timezone.utc) + delta
    try:
        await client.ban_chat_member(message.chat.id, user.id, until_date=until)
        await message.reply_text(_format_success(f"Ban for {time_arg}", message, user.id, user.first_name, reason))
    except ChatAdminRequired:
        await message.reply_text("I need ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")