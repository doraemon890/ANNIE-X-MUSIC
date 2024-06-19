from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid, BadRequest

import datetime
from ANNIEMUSIC import app

def mention(user, name, mention=True):
    if mention:
        link = f"[{name}](tg://openmessage?user_id={user})"
    else:
        link = f"[{name}](https://t.me/{user})"
    return link

async def get_userid_from_username(username):
    try:
        user = await app.get_users(username)
    except:
        return None
    return [user.id, user.first_name]

async def ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason, time=None):
    try:
        await app.ban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Make sure that you have given me that right", False
    except UserAdminInvalid:
        return "I won't ban an admin bruh!!", False
    except Exception as e:
        if user_id == 7059759820:
            return "Why should I ban myself? Sorry but I'm not stupid like you", False
        return f"Oops!!\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was banned by {admin_mention}\n\n"
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    if time:
        msg_text += f"Time: `{time}`\n"
    return msg_text, True

async def unban_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.unban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Make sure that you have given me that right"
    except Exception as e:
        return f"Oops!!\n{e}"
    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    return f"{user_mention} was unbanned by {admin_mention}"

async def mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason, time=None):
    try:
        if time:
            mute_end_time = datetime.datetime.now() + time
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions(), mute_end_time)
        else:
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
    except ChatAdminRequired:
        return "Make sure that you have given me that right", False
    except UserAdminInvalid:
        return "I won't mute an admin bruh!!", False
    except Exception as e:
        if user_id == 7059759820:
            return "Why should I mute myself? Sorry but I'm not stupid like you", False
        return f"Oops!!\n{e}", False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    msg_text = f"{user_mention} was muted by {admin_mention}\n\n"
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    if time:
        msg_text += f"Time: `{time}`\n"
    return msg_text, True

async def unmute_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(
                can_send_media_messages=True,
                can_send_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
                can_invite_users=True
            )
        )
    except ChatAdminRequired:
        return "Make sure that you have given me that right"
    except Exception as e:
        return f"Oops!!\n{e}"
    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    return f"{user_mention} was unmuted by {admin_mention}"

@app.on_message(filters.command(["ban"]))
async def ban_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        # Extract the user ID from the command or reply
        if len(message.command) > 1:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                first_name = message.reply_to_message.from_user.first_name
                reason = message.text.split(None, 1)[1]
            else:
                try:
                    user_id = int(message.command[1])
                    first_name = "User"
                except:
                    user_obj = await get_userid_from_username(message.command[1])
                    if not user_obj:
                        return await message.reply_text("I can't find that user")
                    user_id = user_obj[0]
                    first_name = user_obj[1]
                reason = message.text.partition(message.command[1])[2] or None
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
            reason = None
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message")
        
        msg_text, result = await ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to ban someone")

@app.on_message(filters.command(["unban"]))
async def unban_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        # Extract the user ID from the command or reply
        if len(message.command) > 1:
            try:
                user_id = int(message.command[1])
                first_name = "User"
            except:
                user_obj = await get_userid_from_username(message.command[1])
                if not user_obj:
                    return await message.reply_text("I can't find that user")
                user_id = user_obj[0]
                first_name = user_obj[1]
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message")
        
        msg_text = await unban_user(user_id, first_name, admin_id, admin_name, chat_id)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to unban someone")

@app.on_message(filters.command(["mute"]))
async def mute_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        # Extract the user ID from the command or reply
        if len(message.command) > 1:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                first_name = message.reply_to_message.from_user.first_name
                reason = message.text.split(None, 1)[1]
            else:
                try:
                    user_id = int(message.command[1])
                    first_name = "User"
                except:
                    user_obj = await get_userid_from_username(message.command[1])
                    if not user_obj:
                        return await message.reply_text("I can't find that user")
                    user_id = user_obj[0]
                    first_name = user_obj[1]
                reason = message.text.partition(message.command[1])[2] or None
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
            reason = None
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message")
        
        msg_text, result = await mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to mute someone")

@app.on_message(filters.command(["unmute"]))
async def unmute_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        # Extract the user ID from the command or reply
        if len(message.command) > 1:
            try:
                user_id = int(message.command[1])
                first_name = "User"
            except:
                user_obj = await get_userid_from_username(message.command[1])
                if not user_obj:
                    return await message.reply_text("I can't find that user")
                user_id = user_obj[0]
                first_name = user_obj[1]
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message")
        
        msg_text = await unmute_user(user_id, first_name, admin_id, admin_name, chat_id)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to unmute someone")

@app.on_message(filters.command(["tmute"]))
async def tmute_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_restrict_members:
        # Extract the user ID from the command or reply
        if len(message.command) > 1:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                first_name = message.reply_to_message.from_user.first_name
                time = message.text.split(None, 1)[1]

                try:
                    time_amount = int(time[:-1])
                except:
                    return await message.reply_text("Wrong format!!\nFormat: `/tmute 2m`")

                if time[-1] == "m":
                    mute_duration = datetime.timedelta(minutes=time_amount)
                elif time[-1] == "h":
                    mute_duration = datetime.timedelta(hours=time_amount)
                elif time[-1] == "d":
                    mute_duration = datetime.timedelta(days=time_amount)
                else:
                    return await message.reply_text("Wrong format!!\nFormat:\nm: Minutes\nh: Hours\nd: Days")
            else:
                try:
                    user_id = int(message.command[1])
                    first_name = "User"
                except:
                    user_obj = await get_userid_from_username(message.command[1])
                    if not user_obj:
                        return await message.reply_text("I can't find that user")
                    user_id = user_obj[0]
                    first_name = user_obj[1]

                time = message.text.partition(message.command[1])[2].strip()
                try:
                    time_amount = int(time[:-1])
                except:
                    return await message.reply_text("Wrong format!!\nFormat: `/tmute 2m`")

                if time[-1] == "m":
                    mute_duration = datetime.timedelta(minutes=time_amount)
                elif time[-1] == "h":
                    mute_duration = datetime.timedelta(hours=time_amount)
                elif time[-1] == "d":
                    mute_duration = datetime.timedelta(days=time_amount)
                else:
                    return await message.reply_text("Wrong format!!\nFormat:\nm: Minutes\nh: Hours\nd: Days")
        else:
            return await message.reply_text("Please specify a valid user or reply to that user's message\nFormat: /tmute <username> <time>")
        
        msg_text, result = await mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason=None, time=mute_duration)
        await message.reply_text(msg_text)
    else:
        await message.reply_text("You don't have permission to mute someone")
