import csv
from io import StringIO, BytesIO
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AnnieXMedia import app
from AnnieXMedia.utils.admin_filters import admin_filter

async def collect_members(chat_id, processing_msg):
    members_list = []
    async for member in app.get_chat_members(chat_id):
        members_list.append({
            "username": member.user.username or member.user.first_name,
            "userid": member.user.id
        })
        if len(members_list) % 100 == 0:
            try:
                await processing_msg.edit_text(f"Collected {len(members_list)} members so far...")
            except Exception:
                pass
    return members_list

# ─── /user Command ──────────────────────────────────────────────

@app.on_message(filters.command("user") & admin_filter)
async def user_command(_, message):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("CSV", callback_data="members_csv"),
            InlineKeyboardButton("TXT", callback_data="members_txt")
        ]]
    )
    await message.reply_text(
        "In which format do you want the members list?",
        reply_markup=keyboard
    )

# ─── Callback Query Handler for the /user Command ───────────────

@app.on_callback_query(filters.regex("^members_"))
async def members_format_callback(_, callback_query):
    format_choice = callback_query.data.split("_")[1].lower()
    
    await callback_query.answer()
    
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    processing_msg = await callback_query.message.reply_text("Collecting members, please wait...")
    chat_id = callback_query.message.chat.id

    members_list = await collect_members(chat_id, processing_msg)

    if format_choice == "csv":
        csv_text = StringIO()
        writer = csv.DictWriter(csv_text, fieldnames=["username", "userid"])
        writer.writeheader()
        for member in members_list:
            writer.writerow(member)
        csv_str = csv_text.getvalue()
        file_bytes = BytesIO(csv_str.encode("utf-8"))
        file_name = "members.csv"
        caption_text = "Here is the list of chat members in CSV format."
    else:
        text_lines = [f"{member['username']} - {member['userid']}" for member in members_list]
        txt_str = "\n".join(text_lines)
        file_bytes = BytesIO(txt_str.encode("utf-8"))
        file_name = "members.txt"
        caption_text = "Here is the list of chat members in TXT format."

    file_bytes.seek(0)

    await app.send_document(
        chat_id,
        document=file_bytes,
        caption=caption_text,
        file_name=file_name
    )
    
    await processing_msg.delete()

    try:
        await callback_query.message.delete()
    except Exception:
        pass
