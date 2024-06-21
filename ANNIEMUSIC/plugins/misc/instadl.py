# <============================================== IMPORTS =========================================================>
from telegram import Update, Bot
import httpx

from ANNIEMUSIC import app
from pyrogram import filters

# <=======================================================================================================>

DOWNLOADING_STICKER_ID = (
    "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
)
API_URL = "https://karma-api2.vercel.app/instadl"  # Replace with your actual API URL


# <================================================ FUNCTION =======================================================>
@app.on_message(filters.command(["ig", "insta"]))
async def instadl_command_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /insta [Instagram URL]")
        return

    link = message.command[1]
    try:
        downloading_sticker = await message.reply_sticker(DOWNLOADING_STICKER_ID)

        # Make an asynchronous GET request to the API using httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, params={"url": link})
            response.raise_for_status()
            data = response.json()

        # Check if the API request was successful
        if "content_url" in data:
            content_url = data["content_url"]

            # Determine content type from the URL
            content_type = "video" if "video" in content_url else "photo"

            # Reply with either photo or video
            if content_type == "photo":
                await message.reply_photo(content_url)
            elif content_type == "video":
                await message.reply_video(content_url)
            else:
                await message.reply_text("Unsupported content type.")
        else:
            await message.reply_text(
                "Unable to fetch content. Please check the Instagram URL or try with another Instagram link."
            )

    except Exception as e:
        print(e)
        await message.reply_text(
            "An error occurred while processing the request."
        )

    finally:
        await downloading_sticker.delete()
# <================================================ END =======================================================>
