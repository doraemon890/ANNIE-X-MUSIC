# Authored By Certified Coders © 2025
import asyncio

from pyrogram import filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message, ChatInviteLink
)
from pyrogram.errors import (
    UserNotParticipant, ChatAdminRequired, FloodWait,
    PeerIdInvalid, ChannelPrivate, MessageNotModified, MessageIdInvalid
)
from pyrogram.types import ChatAdministratorRights as _Priv

from AnnieXMedia import app
from AnnieXMedia.logging import LOGGER as _LOGGER_FACTORY
from AnnieXMedia.misc import SUDOERS
from AnnieXMedia.utils.database import get_assistant
from AnnieXMedia.utils.permissions import is_owner_or_sudoer, mention

log = _LOGGER_FACTORY(__name__)




def _confirm_kb(cmd: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data=f"{cmd}_yes"),
                                  InlineKeyboardButton("No", callback_data=f"{cmd}_no")]])


async def _safe_edit(cb: CallbackQuery, text: str):
    try:
        await cb.message.edit(text)
        return True
    except (ChannelPrivate, MessageNotModified, MessageIdInvalid, ChatAdminRequired):
        try:
            await cb.answer(text[:200] if len(text) > 200 else text, show_alert=False)
        except Exception:
            pass
        return False
    except Exception:
        try:
            await cb.answer("Operation finished.", show_alert=False)
        except Exception:
            pass
        return False


def _has(bot_member, *flags) -> bool:
    priv = getattr(bot_member, "privileges", None) or getattr(bot_member, "permissions", None)
    return all(bool(getattr(priv, f, False)) for f in flags)


async def _ensure_assistant_present_and_admin(bot_client, assistant, chat_id) -> int:
    ass_me = await assistant.get_me()
    ass_id = ass_me.id
    try:
        member = await bot_client.get_chat_member(chat_id, ass_id)
        if member.status in (enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT):
            raise UserNotParticipant
    except (UserNotParticipant, PeerIdInvalid):
        link: ChatInviteLink = await bot_client.create_chat_invite_link(chat_id, member_limit=1)
        await assistant.join_chat(link.invite_link)
        await asyncio.sleep(1)

    try:
        await bot_client.promote_chat_member(
            chat_id,
            ass_id,
            privileges=_Priv(
                can_delete_messages=True,
                can_manage_chat=True if "can_manage_chat" in _Priv.__annotations__ else False
            )
        )
    except ChatAdminRequired:
        pass
    except Exception as e:
        log.warning("Assistant promote warning: %s", e)

    return ass_id


async def _fast_clear_history(assistant, chat_id) -> bool:
    try:
        await assistant.delete_history(chat_id, revoke=True)
        return True
    except ChatAdminRequired:
        return False
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await assistant.delete_history(chat_id, revoke=True)
            return True
        except Exception:
            return False
    except Exception as e:
        log.warning("delete_history fast path failed: %s", e)
        return False


async def _fallback_batch_delete(assistant, chat_id, skip_ids=set(), concurrency=3, batch_size=100) -> int:
    sem = asyncio.Semaphore(concurrency)
    tasks, count = [], 0

    async def _deleter(ids):
        nonlocal count
        async with sem:
            while True:
                try:
                    await assistant.delete_messages(chat_id, ids)
                    count += len(ids)
                    break
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except ChatAdminRequired:
                    raise
                except Exception as e:
                    log.error("Batch delete error: %s", e)
                    break

    batch = []
    async for msg in assistant.get_chat_history(chat_id):
        if msg.id in skip_ids:
            continue
        batch.append(msg.id)
        if len(batch) >= batch_size:
            tasks.append(asyncio.create_task(_deleter(batch)))
            batch = []
            if len(tasks) >= 10:
                await asyncio.gather(*tasks)
                tasks.clear()

    if batch:
        tasks.append(asyncio.create_task(_deleter(batch)))

    if tasks:
        await asyncio.gather(*tasks)

    return count


@app.on_message(filters.command("deleteall") & filters.group)
async def deleteall_command(client, message: Message):
    ok, owner = await is_owner_or_sudoer(client, message.chat.id, message.from_user.id)
    if not ok:
        owner_mention = mention(owner.id, owner.first_name) if owner else "the owner"
        return await message.reply_text(f"Sorry {message.from_user.mention}, only {owner_mention} can use /deleteall.")

    bot_member = await client.get_chat_member(message.chat.id, client.me.id)
    if not _has(bot_member, "can_delete_messages", "can_invite_users", "can_promote_members"):
        return await message.reply_text("I need to be admin with delete_messages, invite_users & promote_members.")

    await message.reply(f"{message.from_user.mention}, confirm delete all messages?",
                        reply_markup=_confirm_kb("deleteall"))


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
    ass_id = await _ensure_assistant_present_and_admin(client, assistant, chat_id)

    try:
        fast_ok = await _fast_clear_history(assistant, chat_id)
        if fast_ok:
            await _safe_edit(callback, "✅ Cleared full chat history for everyone.")
        else:
            await _safe_edit(callback, "⚠️ Fast clear not permitted by Telegram. Falling back to high‑speed batch deletion…")
            skip = {callback.message.id}
            deleted = await _fallback_batch_delete(assistant, chat_id, skip_ids=skip, concurrency=3, batch_size=100)
            await _safe_edit(callback, f"✅ Deleted approximately {deleted} messages.")
    except ChatAdminRequired:
        await _safe_edit(callback, "❌ Assistant lacks delete rights. Make me able to promote admins.")
    except Exception as e:
        log.error("Delete-all fatal error: %s", e)
        await _safe_edit(callback, f"❌ Failed: {e}")
    finally:
        try:
            try:
                await client.promote_chat_member(chat_id, ass_id, privileges=_Priv())
            except Exception as e:
                log.warning("Assistant demote skipped: %s", e)
            try:
                await assistant.leave_chat(chat_id)
            except Exception:
                pass
        except Exception:
            pass
