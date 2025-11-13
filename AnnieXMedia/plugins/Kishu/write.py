from pyrogram import Client, filters, enums
from pyrogram.types import Message
from datetime import datetime
from config import BOT_USERNAME
from AnnieXMedia import app
import requests


@app.on_message(filters.command("write"))
async def handwrite(_, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(
            "❌ Please provide some text to write.\n\nUse `/write your message` or reply to a message.",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    msg = await message.reply_text("✍️ Please wait...\nWriting your text...")

    try:
        response = requests.get(f"https://apis.xditya.me/write?text={text}")
        if response.status_code != 200:
            raise Exception("API Error")
        image_url = response.url
    except Exception:
        return await msg.edit(
            "❌ Failed to generate handwritten text. Try again later.",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    caption = (
        f"📝 𝒮𝓊𝒸𝒸𝑒𝓈𝓈!\n\n"
        f"✨ 𝒲𝓇𝒾𝓉𝓉𝑒𝓃 𝒷𝓎: [𝐀𝐍𝐍𝐈𝐄](https://t.me/{BOT_USERNAME})\n"
        f"🥀 𝑅𝑒𝓆𝓊𝑒𝓈𝓉𝑒𝒹 𝒷𝓎: {message.from_user.mention}"
    )

    await msg.delete()
    await message.reply_photo(photo=image_url, caption=caption)


@app.on_message(filters.command("day"))
async def date_to_day_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide a date in this format: `/day 1947-08-15`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    input_date = message.command[1].strip()
    try:
        date_object = datetime.strptime(input_date, "%Y-%m-%d")
        day_of_week = date_object.strftime("%A")

        await message.reply_text(
            f"📆 The day of the week for `{input_date}` is **{day_of_week}**.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except ValueError:
        await message.reply_text(
            "❌ Invalid date format. Please use: `/day YYYY-MM-DD`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
