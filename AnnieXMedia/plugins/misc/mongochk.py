# Authored By Certified Coders © 2025
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pymongo import MongoClient

from AnnieXMedia import app

mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

@app.on_message(filters.command("mongochk"))
async def mongo_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/mongochk <your_mongodb_url>`",
            parse_mode=ParseMode.MARKDOWN
        )

    mongo_url = message.command[1]

    if not re.match(mongo_url_pattern, mongo_url):
        return await message.reply_text(
            "❌ **Invalid MongoDB URL format.**\nIt should start with `mongodb://` or `mongodb+srv://`.",
            parse_mode=ParseMode.MARKDOWN
        )

    try:
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        mongo_client.server_info()
        await message.reply_text(
            "✅ **MongoDB URL is valid and connection was successful.**",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.reply_text(
            f"❌ **Failed to connect to MongoDB:**\n`{str(e)}`",
            parse_mode=ParseMode.MARKDOWN
        )
