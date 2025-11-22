# Authored By Certified Coders © 2025
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS, OWNER_ID
from AnnieXMedia import app
from AnnieXMedia.misc import SUDOERS
from AnnieXMedia.utils.database import add_sudo, remove_sudo
from AnnieXMedia.utils.decorators.language import language
from AnnieXMedia.utils.extraction import extract_user

# ─── Add Sudo ─────────────────────────────────────────────

@app.on_message(filters.command(["addsudo"], prefixes=["/", "!", "."]) & filters.user(OWNER_ID))
@language
async def add_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))

    if await add_sudo(user.id):
        if user.id not in SUDOERS:
            SUDOERS.add(user.id)
        return await message.reply_text(_["sudo_2"].format(user.mention))

    await message.reply_text(_["sudo_8"])

# ─── Remove Sudo ───────────────────────────────────────────

@app.on_message(filters.command(["delsudo", "rmsudo"], prefixes=["/", "!", "."]) & filters.user(OWNER_ID))
@language
async def remove_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))

    if await remove_sudo(user.id):
        if user.id in SUDOERS:
            SUDOERS.remove(user.id)
        return await message.reply_text(_["sudo_4"].format(user.mention))

    await message.reply_text(_["sudo_8"])

# ─── Sudo List Entry ───────────────────────────────────────

@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"], prefixes=["/", "!", "."]) & ~BANNED_USERS)
async def sudoers_list(client, message: Message):
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="sudo_list_view")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_video(
        video="https://files.catbox.moe/x7v3k6.mp4",
        caption="**» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.**\n\n**» ɴᴏᴛᴇ:**  ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ.",
        reply_markup=reply_markup
    )

# ─── Callback: View Sudo List ──────────────────────────────

@app.on_callback_query(filters.regex("^sudo_list_view$"))
async def view_sudo_list_callback(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in SUDOERS:
        return await callback_query.answer("ᴏɴʟʏ sᴜᴅᴏᴇʀs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴀᴄᴄᴇss ᴛʜɪs", show_alert=True)

    owner = await app.get_users(OWNER_ID)
    caption = f"**˹ʟɪsᴛ ᴏғ ʙᴏᴛ ᴍᴏᴅᴇʀᴀᴛᴏʀs˼**\n\n**🌹Oᴡɴᴇʀ** ➥ {owner.mention}\n\n"
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ ᴏᴡɴᴇʀ ๏", url=f"tg://openmessage?user_id={OWNER_ID}")]]

    count = 0
    for user_id in SUDOERS:
        if user_id == OWNER_ID:
            continue
        try:
            user = await app.get_users(user_id)
            count += 1
            caption += f"**🎁 Sᴜᴅᴏ {count} »** {user.mention}\n"
            keyboard.append([
                InlineKeyboardButton(f"๏ ᴠɪᴇᴡ sᴜᴅᴏ {count} ๏", url=f"tg://openmessage?user_id={user_id}")
            ])
        except Exception:
            continue

    if count == 0:
        caption += "_No additional sudoers yet._"

    keyboard.append([InlineKeyboardButton("๏ ʙᴀᴄᴋ ๏", callback_data="sudo_list_back")])
    await callback_query.message.edit_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))

# ─── Callback: Back to List Menu ────────────────────────────

@app.on_callback_query(filters.regex("^sudo_list_back$"))
async def back_to_sudo_list_menu(client, callback_query: CallbackQuery):
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="sudo_list_view")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_caption(
        caption="**» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.**\n\n**» ɴᴏᴛᴇ:**  ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ.",
        reply_markup=reply_markup
    )

# ─── Delete All Sudo ───────────────────────────────────────

@app.on_message(filters.command("delallsudo", prefixes=["/", "!", "%", ",", ".", "@", "#"]) & filters.user(OWNER_ID))
@language
async def remove_all_sudo_users(client, message: Message, _):
    removed_count = 0
    for user_id in list(SUDOERS):
        if user_id != OWNER_ID:
            if await remove_sudo(user_id):
                if user_id in SUDOERS:
                    SUDOERS.remove(user_id)
                removed_count += 1
    await message.reply_text(f"Removed {removed_count} users from the sudo list.")
