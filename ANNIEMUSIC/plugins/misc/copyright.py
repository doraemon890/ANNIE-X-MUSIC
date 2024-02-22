from ANNIEMUSIC import app
from pyrogram import Client, filters
from pyrogram.types import Message


keywords_to_delete = ["porn", "xxx", "sex", "NCERT", "XII", "page", "Ans", "meiotic", "divisions", "System.in", "Scanner", "void", "nextInt"]

async def delete_links(message):
    if any(link in message.text for link in ["http", "https", "www."]):
        await message.delete()

async def delete_messages(client, message):
    if any(keyword in message.text for keyword in keywords_to_delete) and len(message.text.split()) > 20:
        await message.delete()

@app.on_message(filters.group & filters.text & ~filters.me)
async def handle_messages(client, message):
    await delete_links(message)
    await delete_messages(client, message)

@app.on_edited_message(filters.group & filters.text & ~filters.me)
async def handle_edited_messages(client, edited_message):
    await delete_links(edited_message)
    await delete_messages(client, edited_message)

@app.on_message(filters.group & filters.text & ~filters.me)
async def delete_long_messages(client, message):
    if len(message.text.split()) >= 20:
        await message.delete()

@app.on_edited_message(filters.group & filters.text & ~filters.me)
async def delete_edited_long_messages(client, edited_message):
    if len(edited_message.text.split()) >= 20:
        await edited_message.delete()


# -------------------------------

async def delete_pdf_files(client, message):
    if message.document and message.document.mime_type == "application/pdf":
        warning_message = f"@{message.from_user.username} ᴍᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ ᴘᴅғ ʙʜᴇᴊ ᴋᴇ,\n ʙʜᴏsᴀᴅɪᴋᴇ ᴄᴏᴘʏʀɪɢʜᴛ ʟᴀɢʏᴇɢᴀ \n\n ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅɪʏᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ.\n\n ᴀʙ @PRADHAN74 ʙʜᴀɪ ᴋᴇ ᴅᴍ ᴍᴇ ᴀᴘɴɪ ᴍᴜᴍᴍʏ ᴋᴏ ʙʜᴇᴊ ᴅᴇ 🍌🍌🍌."
        await message.reply_text(warning_message)
        await message.delete()
    else:  
        pass

@app.on_message(filters.group & filters.document)
async def message_handler(client, message):
    await delete_pdf_files(client, message)

# -----------------------------------------------------------------------------------
