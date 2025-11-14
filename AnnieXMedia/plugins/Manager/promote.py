"""
-------------------------------------------------------------------------
Promotion and demotion commands with edge‑case handling and time‑bound promotions.

• /promote      – limited‑rights promote
• /fullpromote  – full‑rights promote
• /demote       – remove all admin rights
• /tempadmin    – promote for given time, then auto‑demote

All commands accept reply, @username, or user‑ID, with graceful usage hints.
-------------------------------------------------------------------------
"""

import asyncio
from typing import Optional

from pyrogram import filters, enums
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import ChatAdministratorRights, Message

from AnnieXMedia import app
from AnnieXMedia.utils.decorator import admin_required
from AnnieXMedia.utils.permissions import extract_user_and_title, mention, parse_time


# ────────────────────────────────────────────────────────────
# Privilege presets
# ────────────────────────────────────────────────────────────
_LIMITED_PRIVS = ChatAdministratorRights(
    can_change_info=False,
    can_delete_messages=True,
    can_invite_users=True,
    can_pin_messages=True,
    can_restrict_members=False,
    can_promote_members=False,
    can_manage_chat=True,
    can_manage_video_chats=True,
    is_anonymous=False,
)

_FULL_PRIVS = ChatAdministratorRights(
    can_manage_chat=True,
    can_change_info=True,
    can_delete_messages=True,
    can_invite_users=True,
    can_restrict_members=True,
    can_pin_messages=True,
    can_promote_members=True,
    can_manage_video_chats=True,
    is_anonymous=False,
)

_DEMOTE_PRIVS = ChatAdministratorRights(
    can_change_info=False,
    can_delete_messages=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_restrict_members=False,
    can_promote_members=False,
    can_manage_chat=False,
    can_manage_video_chats=False,
    is_anonymous=False,
)

# ────────────────────────────────────────────────────────────
# Usage strings
# ────────────────────────────────────────────────────────────
_USAGES = {
    "promote":     "/promote @user [title] — or reply with /promote [title]",
    "fullpromote": "/fullpromote @user [title] — or reply with /fullpromote [title]",
    "demote":      "/demote @user — or reply with /demote",
    "tempadmin":   "/tempadmin @user <time> [title] — or reply with /tempadmin <time> [title]",
}

def _usage(cmd: str) -> str:
    return _USAGES.get(cmd, "Invalid usage.")

async def _info(msg: Message, text: str):
    await msg.reply_text(text)

def _format_success(action: str, chat: Message, uid: int, name: str, title: Optional[str] = None) -> str:
    chat_name = chat.chat.title
    user_m    = mention(uid, name)
    admin_m   = mention(chat.from_user.id, chat.from_user.first_name)
    text = (
        f"» {action} ᴀ ᴜsᴇʀ ɪɴ {chat_name}\n"
        f" ᴜsᴇʀ  : {user_m}\n"
        f" ᴀᴅᴍɪɴ : {admin_m}"
    )
    if title:
        text += f"\nTitle: {title}"
    return text

# ────────────────────────────────────────────────────────────
# /promote
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("promote"))
@admin_required("can_promote_members")
async def promote_command(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await _info(message, _usage("promote"))

    uid, name, title = await extract_user_and_title(message, client)
    if not uid:
        return

    member = await client.get_chat_member(message.chat.id, uid)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR:
        return await _info(message, "User is already an admin.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=uid,
            privileges=_LIMITED_PRIVS,
        )
        if title:
            try:
                await client.set_administrator_title(message.chat.id, uid, title)
            except ValueError:
                title = "⚠️ Couldn’t set custom title (not a supergroup)"
        await message.reply_text(_format_success("Promoted", message, uid, name, title))
    except ChatAdminRequired:
        await message.reply_text("I need promote permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot promote that user.")

# ────────────────────────────────────────────────────────────
# /fullpromote
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("fullpromote"))
@admin_required("can_promote_members")
async def fullpromote_command(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await _info(message, _usage("fullpromote"))

    uid, name, title = await extract_user_and_title(message, client)
    if not uid:
        return

    member = await client.get_chat_member(message.chat.id, uid)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR:
        return await _info(message, "User is already an admin.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=uid,
            privileges=_FULL_PRIVS,
        )
        if title:
            try:
                await client.set_administrator_title(message.chat.id, uid, title)
            except ValueError:
                title = "⚠️ Couldn’t set custom title (not a supergroup)"
        await message.reply_text(_format_success("Fully promoted", message, uid, name, title))
    except ChatAdminRequired:
        await message.reply_text("I need promote permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot promote that user.")

# ────────────────────────────────────────────────────────────
# /demote
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("demote"))
@admin_required("can_promote_members")
async def demote_command(client, message: Message):
    if len(message.command) == 1 and not message.reply_to_message:
        return await _info(message, _usage("demote"))

    uid, name, _ = await extract_user_and_title(message, client)
    if not uid:
        return

    member = await client.get_chat_member(message.chat.id, uid)
    if member.status != enums.ChatMemberStatus.ADMINISTRATOR:
        return await _info(message, "User is not an admin.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=uid,
            privileges=_DEMOTE_PRIVS,
        )
        await message.reply_text(_format_success("Demoted", message, uid, name))
    except ChatAdminRequired:
        await message.reply_text("I need promote permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot demote that user.")

# ────────────────────────────────────────────────────────────
# /tempadmin
# ────────────────────────────────────────────────────────────
@app.on_message(filters.command("tempadmin"))
@admin_required("can_promote_members")
async def tempadmin_command(client, message: Message):
    if ((not message.reply_to_message and len(message.command) < 3) or
        (message.reply_to_message and len(message.command) < 2)):
        return await _info(message, _usage("tempadmin"))

    if message.reply_to_message:
        user     = message.reply_to_message.from_user
        time_arg = message.command[1]
        title    = message.text.partition(time_arg)[2].strip() or None
    else:
        user = await client.get_users(message.command[1])
        if not user:
            return await message.reply_text("I can’t find that user.")
        time_arg = message.command[2]
        title    = message.text.partition(time_arg)[2].strip() or None

    delta = parse_time(time_arg)
    if not delta:
        return await message.reply_text("Invalid time format. Use s/m/h/d suffix.")

    uid, name = user.id, user.first_name
    member = await client.get_chat_member(message.chat.id, uid)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR:
        return await _info(message, "User is already an admin.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=uid,
            privileges=_FULL_PRIVS,
        )
        if title:
            try:
                await client.set_administrator_title(message.chat.id, uid, title)
            except ValueError:
                title = "⚠️ Couldn’t set custom title (not a supergroup)"
        await message.reply_text(_format_success(f"Temp‑promoted for {time_arg}", message, uid, name, title))
    except ChatAdminRequired:
        return await message.reply_text("I need promote permissions.")
    except UserAdminInvalid:
        return await message.reply_text("I cannot promote that user.")


    async def _auto_demote():
        await asyncio.sleep(delta.total_seconds())
        try:
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=uid,
                privileges=_DEMOTE_PRIVS,
            )
            await client.send_message(
                message.chat.id,
                f"Auto‑demoted {mention(uid, name)} after {time_arg}."
            )
        except Exception:
            pass

    asyncio.create_task(_auto_demote())
