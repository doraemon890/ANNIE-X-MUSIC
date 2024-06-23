from pyrogram import filters
from ANNIEMUSIC import app

@app.on_message(filters.command("goodbye", prefixes=["/", "!"]))
async def farewell_message(client, message):
    message_text = """
    Radhe Radhe 💗

    It's Your Jarvis going off for a very long time period of 1 year

    I'll be back on 20 March 2025 

    Bye and Enjoy Your Everymoment
    """
    await message.reply_text(message_text)
