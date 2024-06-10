import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.utils.database import get_assistant
from ANNIEMUSIC.utils.jarvis_ban import admin_filter

async def join_userbot(app, chat_id, username=None, invite_link=None):
    userbot = await get_assistant(chat_id)
    try:
        if username:
            await userbot.join_chat(username)
        elif invite_link:
            await userbot.join_chat(invite_link)
        return "**✅ Assistant joined.**"
    except Exception as e:
        return str(e)

async def unban_and_join_userbot(app, chat_id, username=None, invite_link=None):
    userbot = await get_assistant(chat_id)
    userbot_member = await app.get_chat_member(chat_id, userbot.id)
    if userbot_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
        await app.unban_chat_member(chat_id, userbot.id)
        try:
            if username:
                await userbot.join_chat(username)
            elif invite_link:
                await userbot.join_chat(invite_link)
            return "**Assistant was banned, but now unbanned and joined the chat ✅**"
        except Exception as e:
            return str(e)
    return "**Assistant is not banned.**"

async def invite_userbot(app, chat_id):
    userbot = await get_assistant(chat_id)
    try:
        invite_link = await app.create_chat_invite_link(chat_id)
        await userbot.join_chat(invite_link.invite_link)
        return "**✅ Assistant joined successfully.**"
    except Exception as e:
        return str(e)

@app.on_message(filters.command(["userbotjoin", "assistantjoin"], prefixes=[".", "/"]) & (filters.group | filters.private) & admin_filter)
async def join_group(app, message):
    chat_id = message.chat.id
    a = await app.get_me()
    done = await message.reply("**Please wait, inviting assistant...**")
    await asyncio.sleep(1)
    chat_member = await app.get_chat_member(chat_id, a.id)

    if message.chat.username:  # Public group
        if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            response = await join_userbot(app, chat_id, username=message.chat.username)
        else:
            response = "**I need admin power to unban and invite my assistant!**"
    else:  # Private group
        if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            userbot_member = await app.get_chat_member(chat_id, (await get_assistant(chat_id)).id)
            if userbot_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                response = await unban_and_join_userbot(app, chat_id, invite_link=await app.create_chat_invite_link(chat_id))
            else:
                response = await invite_userbot(app, chat_id)
        else:
            response = "**I need admin power to invite my assistant.**"

    await done.edit_text(response)

@app.on_message(filters.command("userbotleave", prefixes=[".", "/"]) & filters.group & admin_filter)
async def leave_one(app, message):
    try:
        userbot = await get_assistant(message.chat.id)
        await userbot.leave_chat(message.chat.id)
        await app.send_message(message.chat.id, "**✅ Userbot successfully left this chat.**")
    except Exception as e:
        print(e)

@app.on_message(filters.command(["leaveall"], prefixes=["."]) & SUDOERS)
async def leave_all(app, message):
    left = 0
    failed = 0
    lol = await message.reply("🔄 **Userbot leaving all chats!**")
    try:
        userbot = await get_assistant(message.chat.id)
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1002014167331:
                continue
            try:
                await userbot.leave_chat(dialog.chat.id)
                left += 1
                await lol.edit(f"**Userbot leaving all groups...**\n\n**Left:** {left} chats.\n**Failed:** {failed} chats.")
            except Exception:
                failed += 1
                await lol.edit(f"**Userbot leaving...**\n\n**Left:** {left} chats.\n**Failed:** {failed} chats.")
            await asyncio.sleep(3)
    finally:
        await app.send_message(message.chat.id, f"**✅ Left from:** {left} chats.\n**❌ Failed in:** {failed} chats.")
