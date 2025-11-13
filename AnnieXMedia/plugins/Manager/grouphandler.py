from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnnieXMedia import app
from AnnieXMedia.utils.admin_filters import admin_filter

# ------------------- Utility Functions ------------------- #

def is_group(message: Message) -> bool:
    return message.chat.type not in (ChatType.PRIVATE, ChatType.BOT)

async def has_permission(user_id: int, chat_id: int, permission: str) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return bool(getattr(getattr(member, "privileges", None), permission, False) or getattr(member, "status", "") in ("creator",))
    except Exception:
        return False

def _view_btn(msg: Message):
    try:
        return InlineKeyboardMarkup([[InlineKeyboardButton("📝 ᴠɪᴇᴡ ᴍᴇssᴀɢᴇ", url=msg.link)]])
    except Exception:
        return None

# ------------------- Pin Message ------------------- #

@app.on_message(filters.command("pin") & admin_filter)
async def pin(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")

    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ ɪᴛ!**")

    if not await has_permission(message.from_user.id, message.chat.id, "can_pin_messages"):
        return await message.reply_text("**ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴘɪɴ ᴍᴇssᴀɢᴇs.**")

    try:
        await message.reply_to_message.pin()
        await message.reply_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!**\n\n**ᴄʜᴀᴛ:** {message.chat.title}\n**ᴀᴅᴍɪɴ:** {message.from_user.mention}",
            reply_markup=_view_btn(message.reply_to_message)
        )
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ ᴘɪɴ ᴍᴇssᴀɢᴇ:**\n`{e}`")

# ------------------- Unpin Message ------------------- #

@app.on_message(filters.command("unpin") & admin_filter)
async def unpin(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")

    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɪᴛ!**")

    if not await has_permission(message.from_user.id, message.chat.id, "can_pin_messages"):
        return await message.reply_text("**ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs.**")

    try:
        await message.reply_to_message.unpin()
        await message.reply_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!**\n\n**ᴄʜᴀᴛ:** {message.chat.title}\n**ᴀᴅᴍɪɴ:** {message.from_user.mention}",
            reply_markup=_view_btn(message.reply_to_message)
        )
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇ:**\n`{e}`")

# ------------------- Set / Remove Photo, Title, Description ------------------- #

@app.on_message(filters.command("setphoto") & admin_filter)
async def set_photo(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ.**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ.**")

    target = message.reply_to_message
    file_id = None

    if getattr(target, "photo", None):
        file_id = target.photo.file_id
    elif getattr(target, "document", None) and getattr(target.document, "mime_type", ""):
        if target.document.mime_type.startswith("image/"):
            file_id = target.document.file_id

    if not file_id:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴀɴ ɪᴍᴀɢᴇ (ᴘʜᴏᴛᴏ ᴏʀ ɪᴍᴀɢᴇ ᴅᴏᴄᴜᴍᴇɴᴛ).**")

    try:
        await app.set_chat_photo(chat_id=message.chat.id, photo=file_id)
        await message.reply_text(f"**ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\nʙʏ {message.from_user.mention}")
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ᴘʜᴏᴛᴏ:**\n`{e}`")

@app.on_message(filters.command("removephoto") & admin_filter)
async def remove_photo(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ.**")
    try:
        await app.delete_chat_photo(message.chat.id)
        await message.reply_text(f"**ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ ʀᴇᴍᴏᴠᴇᴅ!**\nʙʏ {message.from_user.mention}")
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘʜᴏᴛᴏ:**\n`{e}`")

@app.on_message(filters.command("settitle") & admin_filter)
async def set_title(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ.**")

    title = None
    if len(message.command) > 1:
        title = message.text.split(None, 1)[1].strip()
    elif message.reply_to_message and getattr(message.reply_to_message, "text", None):
        title = message.reply_to_message.text.strip()

    if not title:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴇᴡ ᴛɪᴛʟᴇ.**")

    try:
        await message.chat.set_title(title)
        await message.reply_text(f"**ɢʀᴏᴜᴘ ɴᴀᴍᴇ ᴄʜᴀɴɢᴇᴅ ᴛᴏ:** {title}\nʙʏ {message.from_user.mention}")
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴛʟᴇ:**\n`{e}`")


@app.on_message(filters.command("setdiscription") & admin_filter)
async def set_description(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ.**")

    desc = None
    if len(message.command) > 1:
        desc = message.text.split(None, 1)[1].strip()
    elif message.reply_to_message and getattr(message.reply_to_message, "text", None):
        desc = message.reply_to_message.text.strip()

    if not desc:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴇᴡ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ.**")

    try:
        await message.chat.set_description(desc)
        await message.reply_text(f"**ɢʀᴏᴜᴘ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇᴅ!**\nʙʏ {message.from_user.mention}")
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**\n`{e}`")
