# Authored By Certified Coders © 2025
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
    ChannelPrivate,
    FloodWait,
    PeerIdInvalid,
    ChatWriteForbidden,
)
from AnnieXMedia import app
from AnnieXMedia.utils.admin_filters import dev_filter, admin_filter, sudo_filter
from AnnieXMedia.utils.database import get_assistant

ACTIVE_STATUSES = {
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.RESTRICTED,
}

async def _is_participant(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ACTIVE_STATUSES
    except (UserNotParticipant, PeerIdInvalid):
        return False
    except Exception as e:
        return False

async def join_userbot(app, chat_id: int, chat_username: str = None) -> str:
    userbot = await get_assistant(chat_id)
    try:
        member = await app.get_chat_member(chat_id, userbot.id)
        if member.status == ChatMemberStatus.BANNED:
            try:
                await app.unban_chat_member(chat_id, userbot.id)
                member = await app.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                return "**❌ I need unban permission to add the assistant.**"
        if member.status in ACTIVE_STATUSES:
            return "**🤖 Assistant is already in the chat.**"
    except (UserNotParticipant, PeerIdInvalid):
        pass

    invite = None
    if chat_username:
        invite = chat_username if chat_username.startswith("@") else f"@{chat_username}"
    else:
        try:
            link = await app.create_chat_invite_link(chat_id)
            invite = link.invite_link
        except ChatAdminRequired:
            return "**❌ I need permission to create invite links or a public @username to add the assistant.**"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            await userbot.join_chat(invite)
            return "**✅ Assistant joined successfully.**"
        except UserAlreadyParticipant:
            return "**🤖 Assistant is already a participant.**"
        except FloodWait as e:
            if attempt == max_retries - 1:
                return f"**❌ Failed to add assistant after retries:** Flood wait exceeded."
            await asyncio.sleep(e.value)
        except Exception as e:
            return f"**❌ Failed to add assistant:** `{str(e)}`"

@app.on_chat_join_request()
async def approve_join_request(client, chat_join_request: ChatJoinRequest):
    userbot = await get_assistant(chat_join_request.chat.id)
    if chat_join_request.from_user.id != userbot.id:
        return

    chat_id = chat_join_request.chat.id
    try:
        if await _is_participant(client, chat_id, userbot.id):
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await client.approve_chat_join_request(chat_id, userbot.id)
                break
            except UserAlreadyParticipant:
                return
            except FloodWait as e:
                if attempt == max_retries - 1:
                    return
                await asyncio.sleep(e.value)
            except (ChatAdminRequired, PeerIdInvalid):
                return

        try:
            await client.send_message(chat_id, "**✅ Assistant has been approved and joined the chat.**")
        except ChatWriteForbidden:
            pass
    except Exception as e:
        pass

@app.on_message(
    filters.command(["userbotjoin", "assistantjoin"], prefixes=[".", "/"])
    & (filters.group | filters.private)
    & admin_filter
    & sudo_filter
)
async def join_group(app, message):
    chat_id = message.chat.id
    status_message = await message.reply("**⏳ Please wait, inviting assistant...**")
    try:
        me = await app.get_me()
        chat_member = await app.get_chat_member(chat_id, me.id)
        if chat_member.status != ChatMemberStatus.ADMINISTRATOR:
            await status_message.edit_text("**❌ I need to be admin to invite the assistant.**")
            return
    except ChatAdminRequired:
        await status_message.edit_text("**❌ I don't have permission to check admin status in this chat.**")
        return
    except Exception as e:
        await status_message.edit_text(f"**❌ Failed to verify permissions:** `{str(e)}`")
        return

    chat_username = message.chat.username or None
    response = await join_userbot(app, chat_id, chat_username)
    try:
        await status_message.edit_text(response)
    except ChatWriteForbidden:
        pass

@app.on_message(
    filters.command("userbotleave", prefixes=[".", "/"])
    & filters.group
    & admin_filter
    & sudo_filter
)
async def leave_one(app, message):
    chat_id = message.chat.id
    try:
        userbot = await get_assistant(chat_id)
        try:
            member = await userbot.get_chat_member(chat_id, userbot.id)
            if member.status not in ACTIVE_STATUSES:
                await message.reply("**🤖 Assistant is not currently in this chat.**")
                return
        except UserNotParticipant:
            await message.reply("**🤖 Assistant is not currently in this chat.**")
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await userbot.leave_chat(chat_id)
                try:
                    await app.send_message(chat_id, "**✅ Assistant has left this chat.**")
                except ChatWriteForbidden:
                    pass
                return
            except FloodWait as e:
                if attempt == max_retries - 1:
                    await message.reply("**❌ Failed to leave after retries: Flood wait exceeded.**")
                    return
                await asyncio.sleep(e.value)
            except ChannelPrivate:
                await message.reply("**❌ Error: This chat is not accessible or has been deleted.**")
                return
            except Exception as e:
                await message.reply(f"**❌ Failed to remove assistant:** `{str(e)}`")
                return
    except Exception as e:
        await message.reply(f"**❌ Unexpected error:** `{str(e)}`")

@app.on_message(filters.command("leaveall", prefixes=["."]) & dev_filter)
async def leave_all(app, message):
    left = 0
    failed = 0
    status_message = await message.reply("🔄 **Assistant is leaving all chats...**")
    try:
        userbot = await get_assistant(message.chat.id)
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1002014167331:
                continue
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await userbot.leave_chat(dialog.chat.id)
                    left += 1
                    break
                except FloodWait as e:
                    if attempt == max_retries - 1:
                        failed += 1
                        break
                    await asyncio.sleep(e.value)
                except Exception:
                    failed += 1
                    break

            try:
                await status_message.edit_text(
                    f"**Leaving chats...**\n✅ Left: `{left}`\n❌ Failed: `{failed}`"
                )
            except ChatWriteForbidden:
                pass
            await asyncio.sleep(0.5)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        pass
    finally:
        try:
            await app.send_message(
                message.chat.id,
                f"**✅ Left from:** `{left}` chats.\n**❌ Failed in:** `{failed}` chats.",
            )
        except ChatWriteForbidden:
            pass
