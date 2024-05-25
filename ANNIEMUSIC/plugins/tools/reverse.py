import asyncio
import os
import uuid

import httpx
from pyrogram.enums import MessageMediaType
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )
from pyrogram import Client, filters


from ANNIEMUSIC import app

ENDPOINT = "https://sasta-api.vercel.app/googleImageSearch"
httpx_client = httpx.AsyncClient(timeout=60)

COMMANDS = [
    "reverse",
    "grs"
    "gis",
    "pp"
    ]

class STRINGS:
    REPLY_TO_MEDIA = "ℹ️ Please reply to a message that contains one of the supported media types, such as a photo, sticker, or image file."
    UNSUPPORTED_MEDIA_TYPE = "⚠️ <b>Unsupported media type!</b>\nℹ️ Please reply with a supported media type: image, sticker, or image file."
    
    REQUESTING_API_SERVER = "📡 Requesting to <b>API Server</b>... 📶"
    
    DOWNLOADING_MEDIA = "⏳ Downloading media..."
    UPLOADING_TO_API_SERVER = "📡 Uploading media to <b>API Server</b>... 📶"
    PARSING_RESULT = "💻 Parsing result..."
    
    EXCEPTION_OCCURRED = "❌ <b>Exception occurred!</b>\n\n<b>Exception:</b> {}"
    
    RESULT = """
🔤 <b>Query:</b> {query}
🔗 <b>Page Link:</b> <a href="{search_url}">Link</a>

⌛️ <b>Time Taken:</b> <code>{time_taken}</code> ms.
🧑‍💻 <b>Credits:</b> @KangersNetwork
    """
    OPEN_SEARCH_PAGE = "↗️ Open Search Page"

@app.on_message(filters.command(COMMANDS))
async def on_google_lens_search(client: Client, message: Message) -> None:
    if len(message.command) > 1:
        image_url = message.command[1]
        params = {
            "image_url": image_url
        }
        status_msg = await message.reply(STRINGS.REQUESTING_API_SERVER)
        start_time = asyncio.get_event_loop().time()
        response = await httpx_client.get(ENDPOINT, params=params)
        
    elif (reply := message.reply_to_message):
        if reply.media not in (MessageMediaType.PHOTO, MessageMediaType.STICKER, MessageMediaType.DOCUMENT):
            await message.reply(STRINGS.UNSUPPORTED_MEDIA_TYPE)
            return
        
        status_msg = await message.reply(STRINGS.DOWNLOADING_MEDIA)
        file_path = f"temp/{uuid.uuid4()}"
        try:
            await reply.download(file_path)
        except Exception as exc:
            text = STRINGS.EXCEPTION_OCCURRED.format(exc)
            await message.reply(text)
            
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            return
        
        with open(file_path, "rb") as image_file:
            start_time = asyncio.get_event_loop().time()
            files = {"file": image_file}
            await status_msg.edit(STRINGS.UPLOADING_TO_API_SERVER)
            response = await httpx_client.post(ENDPOINT, files=files)
        
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
    
    if response.status_code == 404:
        text = STRINGS.EXCEPTION_OCCURRED.format(response.json()["error"])
        await message.reply(text)
        await status_msg.delete()
        return
    elif response.status_code != 200:
        text = STRINGS.EXCEPTION_OCCURRED.format(response.text)
        await message.reply(text)
        await status_msg.delete()
        return
    
    await status_msg.edit(STRINGS.PARSING_RESULT)
    response_json = response.json()
    query = response_json["query"]
    search_url = response_json["search_url"]
    
    end_time = asyncio.get_event_loop().time() - start_time
    time_taken = "{:.2f}".format(end_time)
    
    text = STRINGS.RESULT.format(
        query=f"<code>{query}</code>" if query else "<i>Name not found</i>",
        search_url=search_url,
        time_taken=time_taken
        )
    buttons = [
        [InlineKeyboardButton(STRINGS.OPEN_SEARCH_PAGE, url=search_url)]
        ]
    await message.reply(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
    await status_msg.delete()