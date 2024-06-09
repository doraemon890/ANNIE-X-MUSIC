import requests
import random
from ANNIEMUSIC import app, userbot
from ANNIEMUSIC.misc import SUDOERS
from pyrogram import *
from pyrogram.types import *
from ANNIEMUSIC.utils.jarvis_ban import admin_filter

Jarvis_text = [
    "hey please don't disturb me.",
    "who are you",    
    "aap kon ho",
    "aap mere owner to nhi lgte ",
    "hey tum mera name kyu le rhe ho meko sone do",
    "ha bolo kya kaam hai ",
    "dekho abhi mai busy hu ",
    "hey i am busy",
    "aapko smj nhi aata kya ",
    "leave me alone",
    "dude what happend",    
]

strict_txt = [
    "i can't restrict against my besties",
    "are you serious i am not restrict to my friends",
    "fuck you bsdk k mai apne dosto ko kyu kru",
    "hey stupid admin ", 
    "ha ye phele krlo maar lo ek dusre ki gwaand",  
    "i can't hi is my closest friend",
    "i love him please don't restict this user try to usertand "
]

ban = ["ban","boom"]
unban = ["unban",]
mute = ["mute","silent","shut"]
unmute = ["unmute","speak","free"]
kick = ["kick", "out","nikaal","nikal"]
promote = ["promote","adminship"]
fullpromote = ["fullpromote","fulladmin"]
demote = ["demote","lelo"]
lock = ["lock"]
unlock = ["unlock"]
lockable_content = ["text", "video", "audio", "photo", "document", "sticker"]

@app.on_message(filters.command(["nnie"], prefixes=["A", "a"]) & admin_filter)
async def restriction_app(app: app, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if len(message.text) < 2:
        return await message.reply(random.choice(Jarvis_text))
    bruh = message.text.split(maxsplit=1)[1]
    data = bruh.split(" ")
    
    if reply:
        user_id = reply.from_user.id
        for banned in data:
            print(f"present {banned}")
            if banned in ban:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))          
                else:
                    await app.ban_chat_member(chat_id, user_id)
                    await message.reply("OK, Ban kar diya madrchod ko sala Chutiya tha !")
                    
        for unbanned in data:
            print(f"present {unbanned}")
            if unbanned in unban:
                await app.unban_chat_member(chat_id, user_id)
                await message.reply(f"Ok, aap bolte hai to unban kar diya") 
                
        for kicked in data:
            print(f"present {kicked}")
            if kicked in kick:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))
                else:
                    await app.ban_chat_member(chat_id, user_id)
                    await app.unban_chat_member(chat_id, user_id)
                    await message.reply("get lost! bhga diya bhosdi wale ko") 
                    
        for muted in data:
            print(f"present {muted}") 
            if muted in mute:
                if user_id in SUDOERS:
                    await message.reply(random.choice(strict_txt))
                else:
                    permissions = ChatPermissions(can_send_messages=False)
                    await message.chat.restrict_member(user_id, permissions)
                    await message.reply(f"muted successfully! Disgusting people.") 
                    
        for unmuted in data:
            print(f"present {unmuted}")            
            if unmuted in unmute:
                permissions = ChatPermissions(can_send_messages=True)
                await message.chat.restrict_member(user_id, permissions)
                await message.reply(f"Huh, OK, sir!")   

        for promoted in data:
            print(f"present {promoted}")            
            if promoted in promote:
                await app.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=False,
                    can_pin_messages=True,
                    can_promote_members=False,
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                ))
                await message.reply("promoted !")

        for demoted in data:
            print(f"present {demoted}")            
            if demoted in demote:
                await app.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                ))
                await message.reply("demoted !")

        for fullpromoted in data:
            print(f"present {fullpromoted}")            
            if fullpromoted in fullpromote:
                await app.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(
                    can_change_info=True,
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                ))
                await message.reply("fullpromoted !")
                
        for lock_action in data:
            print(f"present {lock_action}")
            if lock_action in lock:
                if "text" in data:
                    permissions = ChatPermissions(can_send_messages=False)
                elif "video" in data:
                    permissions = ChatPermissions(can_send_media_messages=False)
                elif "audio" in data:
                    permissions = ChatPermissions(can_send_other_messages=False)
                elif "photo" in data:
                    permissions = ChatPermissions(can_send_photos=False)
                elif "document" in data:
                    permissions = ChatPermissions(can_send_documents=False)
                elif "sticker" in data:
                    permissions = ChatPermissions(can_send_stickers=False)
                await app.set_chat_permissions(chat_id, permissions)
                await message.reply(f"Locked {data[2]} content!")

        for unlock_action in data:
            print(f"present {unlock_action}")
            if unlock_action in unlock:
                if "text" in data:
                    permissions = ChatPermissions(can_send_messages=True)
                elif "video" in data:
                    permissions = ChatPermissions(can_send_media_messages=True)
                elif "audio" in data:
                    permissions = ChatPermissions(can_send_other_messages=True)
                elif "photo" in data:
                    permissions = ChatPermissions(can_send_photos=True)
                elif "document" in data:
                    permissions = ChatPermissions(can_send_documents=True)
                elif "sticker" in data:
                    permissions = ChatPermissions(can_send_stickers=True)
                await app.set_chat_permissions(chat_id, permissions)
                await message.reply(f"Unlocked {data[2]} content!")

