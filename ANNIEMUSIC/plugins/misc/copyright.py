from ANNIEMUSIC import app
from pyrogram import Client, filters
from pyrogram.types import Message
from ANNIEMUSIC.plugins.misc.CP import CP


keywords_to_delete = CP

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
