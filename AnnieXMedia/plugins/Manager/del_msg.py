
"""
-------------------------------------------------------------------------
Delete all group messages using an assistant account, with owner-only confirmation.

• /deleteall – prompts the owner for confirmation, then clears the chat history via assistant.
  Uses `assistant.delete_chat_history(chat_id, revoke=True)` under the hood.
  Falls back to manual batch deletion if needed.
-------------------------------------------------------------------------
"""

import asyncio

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message, ChatInviteLink, ChatPrivileges
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    UserNotParticipant, ChatAdminRequired, FloodWait,
    PeerIdInvalid, ChannelPrivate, MessageNotModified, MessageIdInvalid
)

from AnnieXMedia import app
from AnnieXMedia.logging import LOGGER as _LOGGER_FACTORY
from AnnieXMedia.misc import SUDOERS
from AnnieXMedia.utils.database import get_assistant
from AnnieXMedia.utils.permissions import is_owner_or_sudoer, mention

log = _LOGGER_FACTORY(__name__)


def _confirm_kb(cmd: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=f"{cmd}_yes"),
            InlineKeyboardButton("No", callback_data=f"{cmd}_no"),
        ]
    ])


async def _safe_edit(cb: CallbackQuery, text: str):
    try:
        await cb.message.edit(text)
        return True
    except (ChannelPrivate, MessageNotModified, MessageIdInvalid, ChatAdminRequired) as e:
        log.warning("Safe edit suppressed error: %s", e)
        try:
            await cb.answer(text[:200] if len(text) > 200 else text, show_alert=False)
        except Exception:
            pass
        return False
    except Exception as e:
        log.error("Unexpected edit error: %s", e)
        try:
            await cb.answer("Operation finished.", show_alert=False)
        except Exception:
            pass
        return False


@app.on_message(filters.command("deleteall") & filters.group)
async def deleteall_command(client, message: Message):
    ok, owner = await is_owner_or_sudoer(client, message.chat.id, message.from_user.id)
    if not ok:
        owner_mention = mention(owner.id, owner.first_name) if owner else "the owner"
        return await message.reply_text(
            f"Sorry {message.from_user.mention}, only {owner_mention} can use /deleteall."
        )

    bot_member = await client.get_chat_member(message.chat.id, client.me.id)
    priv = bot_member.privileges
    if not (priv.can_delete_messages and priv.can_invite_users and priv.can_promote_members):
        return await message.reply_text(
            "I need to be admin with delete_messages, invite_users & promote_members."
        )

    await message.reply(
        f"{message.from_user.mention}, confirm delete all messages?",
        reply_markup=_confirm_kb("deleteall")
    )


@app.on_callback_query(filters.regex(r"^deleteall_(yes|no)$"))
async def deleteall_callback(client, callback: CallbackQuery):
    _, ans = callback.data.split("_")
    chat_id = callback.message.chat.id
    uid = callback.from_user.id

    ok, _ = await is_owner_or_sudoer(client, chat_id, uid)
    if not ok:
        return await callback.answer("Only the group owner can confirm.", show_alert=True)

    if ans == "no":
        await _safe_edit(callback, "Delete all canceled.")
        return

    await _safe_edit(callback, "⏳ Deleting all messages...")

    assistant = await get_assistant(chat_id)
    ass_me = await assistant.get_me()
    ass_id = ass_me.id

    try:
        member = await client.get_chat_member(chat_id, ass_id)
        if member.status in (ChatMemberStatus.BANNED, ChatMemberStatus.LEFT):
            raise UserNotParticipant
    except (UserNotParticipant, PeerIdInvalid):
        try:
            link: ChatInviteLink = await client.create_chat_invite_link(chat_id, member_limit=1)
            await assistant.join_chat(link.invite_link)
            await asyncio.sleep(1)
        except ChatAdminRequired:
            await _safe_edit(callback, "Failed to invite assistant: missing invite permission.")
            return
        except Exception as e:
            log.error("Invite assistant error: %s", e)
            await _safe_edit(callback, f"Failed to add assistant: {e}")
            return

    try:
        await client.promote_chat_member(
            chat_id, ass_id,
            privileges=ChatPrivileges(can_delete_messages=True)
        )
    except ChatAdminRequired:
        await _safe_edit(callback, "Failed to promote assistant: missing promote permission.")
        return
    except Exception as e:
        log.error("Promote assistant error: %s", e)
        await _safe_edit(callback, f"Failed to promote assistant: {e}")
        return

    try:
        deleted_count: int = await assistant.delete_chat_history(chat_id, revoke=True)
        await _safe_edit(callback, f"✅ Deleted {deleted_count} messages successfully.")
        try:
            await client.promote_chat_member(chat_id, ass_id, privileges=ChatPrivileges())
        except Exception as e:
            log.warning("Assistant demote skipped: %s", e)
        try:
            await assistant.leave_chat(chat_id)
        except Exception:
            pass
        return
    except ChatAdminRequired:
        await _safe_edit(callback, "⚠️ Cannot clear full history via API (missing admin rights). Falling back to batch deletion...")
    except Exception as e:
        log.error("delete_chat_history failed: %s", e)

    await _fallback_batch_delete(client, assistant, callback)


async def _fallback_batch_delete(client, assistant, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    await _safe_edit(callback, "Fallback: batch-deleting messages…")
    batch, count = [], 0

    async for msg in assistant.get_chat_history(chat_id):
        if msg.id == callback.message.id:
            continue
        batch.append(msg.id)
        if len(batch) >= 100:
            try:
                await assistant.delete_messages(chat_id, batch)
                count += len(batch)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                log.error("Batch delete error: %s", e)
            batch.clear()

    if batch:
        try:
            await assistant.delete_messages(chat_id, batch)
            count += len(batch)
        except Exception as e:
            log.error("Final batch delete error: %s", e)

    try:
        await _safe_edit(callback, f"✅ Fallback deleted approx. {count} messages.")
    finally:
        ass_id = (await assistant.get_me()).id
        try:
            try:
                await client.promote_chat_member(chat_id, ass_id, privileges=ChatPrivileges())
            except Exception as e:
                log.warning("Assistant demote skipped: %s", e)
            await assistant.leave_chat(chat_id)
        except Exception:
            pass