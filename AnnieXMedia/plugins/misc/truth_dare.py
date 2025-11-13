from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import httpx
from AnnieXMedia import app

TRUTH_API = "https://api.truthordarebot.xyz/v1/truth"
DARE_API = "https://api.truthordarebot.xyz/v1/dare"


@app.on_message(filters.command("truth"))
async def get_truth(client: Client, message: Message):
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            res = await http.get(TRUTH_API)
        if res.status_code == 200:
            question = res.json().get("question", "No question found.")
            await message.reply_text(
                f"🔎 **Truth:**\n\n{question}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text("❌ Failed to fetch a truth question.")
    except Exception as e:
        print(f"Truth error: {e}")
        await message.reply_text("⚠️ Error occurred while fetching a truth question.")


@app.on_message(filters.command("dare"))
async def get_dare(client: Client, message: Message):
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            res = await http.get(DARE_API)
        if res.status_code == 200:
            question = res.json().get("question", "No question found.")
            await message.reply_text(
                f"🎯 **Dare:**\n\n{question}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply_text("❌ Failed to fetch a dare question.")
    except Exception as e:
        print(f"Dare error: {e}")
        await message.reply_text("⚠️ Error occurred while fetching a dare question.")
