import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from ANNIEMUSIC import app
from ANNIEMUSIC.misc import SUDOERS
from ANNIEMUSIC.utils.database import get_assistant
from ANNIEMUSIC.utils.jarvis_ban import admin_filter

@app.on_message(filters.group & filters.command(["userbotjoin", "assistantjoin"], prefixes=["."]) & ~filters.private)
async def join_group(app, message):
    a = await app.get_me()
    chat_id = message.chat.id
    userbot = await get_assistant(chat_id)
    userbot_id = userbot.id
    done = await message.reply("**Please wait, inviting assistant...**")
    await asyncio.sleep(1)
    chat_member = await app.get_chat_member(chat_id, a.id)

    if message.chat.username and chat_member.status != ChatMemberStatus.ADMINISTRATOR:
        try:
            await userbot.join_chat(message.chat.username)
            await done.edit_text("**✅ Assistant joined.**")
        except Exception:
            await done.edit_text("**I need admin power to unban and invite my assistant!**")

    elif message.chat.username and chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        try:
            await userbot.join_chat(message.chat.username)
            await done.edit_text("**✅ Assistant joined.**")
        except Exception as e:
            await done.edit_text(str(e))

    elif not message.chat.username and chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        try:
            userbot_member = await app.get_chat_member(chat_id, userbot_id)
            if userbot_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                await app.unban_chat_member(chat_id, userbot_id)
                await done.edit_text("**Assistant is unbanned, joining...**")
                await userbot.join_chat(message.chat.username)
                await done.edit_text("**Assistant was banned, but now unbanned and joined the chat ✅**")
        except Exception as e:
            await done.edit_text(
                "**Failed to join, please give ban power and invite user power or unban assistant manually then try again with /userbotjoin**"
            )
        return

    elif not message.chat.username and chat_member.status != ChatMemberStatus.ADMINISTRATOR:
        await done.edit_text("**I need admin power to invite my assistant.**")

    elif not message.chat.username and chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        try:
            try:
                userbot_member = await app.get_chat_member(chat_id, userbot_id)
                if userbot_member.status not in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                    await done.edit_text("**✅ Assistant already joined.**")
                    return
            except Exception:
                invite_link = await app.create_chat_invite_link(chat_id)
                await asyncio.sleep(2)
                await userbot.join_chat(invite_link.invite_link)
                await done.edit_text("**✅ Assistant joined successfully.**")
        except Exception as e:
            await done.edit_text(
                f"**I found that my assistant has not joined this group and I am not able to invite my assistant because I don't have invite user admin power. Please provide invite user admin power and try again with /userbotjoin.**\n\n**ID »** @{userbot.username}"
            )

    elif not message.chat.username and chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        try:
            userbot_member = await app.get_chat_member(chat_id, userbot_id)
            if userbot_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                await app.unban_chat_member(chat_id, userbot_id)
                await done.edit_text("**Assistant is unbanned, type again: /userbotjoin.**")
                invite_link = await app.create_chat_invite_link(chat_id)
                await asyncio.sleep(2)
                await userbot.join_chat(invite_link.invite_link)
                await done.edit_text("**Assistant was banned, now unbanned, and joined chat ✅**")
        except Exception as e:
            await done.edit_text(
                f"**I found that my assistant is banned in this group and I am not able to unban my assistant because I don't have ban power. Please provide ban power or unban my assistant manually then try again with /userbotjoin.**\n\n**ID »** @{userbot.username}"
            )
        return

@app.on_message(filters.command("userbotleave", prefixes=["."]) & filters.group & admin_filter)
async def leave_one(app, message):
    try:
        userbot = await get_assistant(message.chat.id)
        await userbot.leave_chat(message.chat.id)
        await app.send_message(message.chat.id, "**✅ Userbot successfully left this chat.**")
    except Exception as e:
        print(e)

@app.on_message(filters.command(["leaveall"], prefixes=["."]) & SUDOERS)
async def leave_all(app, message):
    if message.from_user.id not in SUDOERS:
        return

    left = 0
    failed = 0
    lol = await message.reply("🔄 **Userbot leaving all chats!**")
    try:
        userbot = await get_assistant(message.chat.id)
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1001733534088:
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
