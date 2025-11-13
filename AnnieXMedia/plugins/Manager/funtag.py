import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait
from AnnieXMedia import app
from AnnieXMedia.utils.admin_check import is_admin
from AnnieXMedia.plugins.misc.funtag_messages import (
    GN_MESSAGES,
    GM_MESSAGES,
    HI_MESSAGES,
    QUOTES,
    SHAYARI,
    TAG_ALL,
)

spam_chats = set()
active_tags = {}

async def mention_members(client, message, message_pool, stop_cmd):
    chat_id = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("❗ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs.")

    if not await is_admin(message):
        return await message.reply_text("🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    if chat_id in spam_chats:
        stop_command = active_tags.get(chat_id, "tagstop")
        return await message.reply_text(
            f"⚠️ ᴀ ᴛᴀɢɢɪɴɢ sᴇssɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ.\n"
            f"➤ ᴜsᴇ /{stop_command} ᴛᴏ sᴛᴏᴘ ɪᴛ."
        )

    spam_chats.add(chat_id)
    active_tags[chat_id] = stop_cmd

    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in spam_chats:
                break
            if member.user.is_bot:
                continue
            try:
                await client.send_message(
                    chat_id,
                    f"[{member.user.first_name}](tg://user?id={member.user.id}) {random.choice(message_pool)}",
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(4)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error tagging user: {e}")
                continue
    finally:
        spam_chats.discard(chat_id)
        active_tags.pop(chat_id, None)
        await client.send_message(chat_id, "✅ ᴛᴀɢɢɪɴɢ sᴇssɪᴏɴ ᴇɴᴅᴇᴅ.")

@app.on_message(filters.command("gntag", prefixes=["/", "!"]))
async def gntag(client, message):
    await mention_members(client, message, GN_MESSAGES, "gnstop")

@app.on_message(filters.command("gmtag", prefixes=["/", "!"]))
async def gmtag(client, message):
    await mention_members(client, message, GM_MESSAGES, "gmstop")

@app.on_message(filters.command("hitag", prefixes=["/", "!"]))
async def hitag(client, message):
    await mention_members(client, message, HI_MESSAGES, "histop")

@app.on_message(filters.command("lifetag", prefixes=["/", "!"]))
async def lifetag(client, message):
    await mention_members(client, message, QUOTES, "lifestop")

@app.on_message(filters.command("shayari", prefixes=["/", "!"]))
async def shayari_tag(client, message):
    await mention_members(client, message, SHAYARI, "shayarioff")

@app.on_message(filters.command("tagall", prefixes=["/", "!"]))
async def tag_all(client, message):
    await mention_members(client, message, TAG_ALL, "tagoff")

@app.on_message(filters.command(["gmstop", "gnstop", "histop", "lifestop", "shayarioff", "tagoff", "tagstop"], prefixes=["/", "!"]))
async def stop_tagging(client, message):
    chat_id = message.chat.id

    if not await is_admin(message):
        return await message.reply_text("🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴛᴏᴘ ᴛᴀɢɢɪɴɢ.")

    if chat_id not in spam_chats:
        return await message.reply_text("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀɢɢɪɴɢ sᴇssɪᴏɴ ғᴏᴜɴᴅ.")

    spam_chats.discard(chat_id)
    active_tags.pop(chat_id, None)
    await message.reply_text("✅ ᴍᴇɴᴛɪᴏɴɪɴɢ sᴛᴏᴘᴘᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.")
