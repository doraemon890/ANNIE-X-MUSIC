# Authored By Certified Coders © 2025
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from AnnieXMedia import app
import httpx

BORED_API_URL = "https://apis.scrimba.com/bored/api/activity"

@app.on_message(filters.command("bored"))
async def bored_command(client: Client, message: Message):
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            response = await http.get(BORED_API_URL)

        if response.status_code != 200:
            return await message.reply_text(
                "❌ Failed to fetch a fun activity. Try again later.",
            )

        data = response.json()
        activity = data.get("activity")

        if activity:
            await message.reply_text(
                f"😐 **Feeling bored?**\n\n🎯 **Try this:** `{activity}`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text("🤷 No activity found.")

    except Exception as e:
        print(f"Bored API error: {e}")
        await message.reply_text(
            "⚠️ Something went wrong while fetching boredom busters.",
        )
