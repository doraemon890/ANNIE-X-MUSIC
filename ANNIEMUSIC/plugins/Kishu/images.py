import requests
from requests import get
from ANNIEMUSIC import app
from pyrogram import filters
from pyrogram.types import InputMediaPhoto

UNSPLASH_API_KEY = 'UwPT7-Of5XQgwxHx-GfcXa4sK0O_38Pbi-6FrQ5f7AY'

@app.on_message(filters.command(["imr"], prefixes=["/", "!"]))
async def pinterest(_, message):
    chat_id = message.chat.id

    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("ɢɪᴠᴇ ɪᴍᴀɢᴇ ɴᴀᴍᴇ ғᴏʀ sᴇᴀʀᴄʜ 🔍")

    response = get(f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_API_KEY}")

    if response.status_code != 200:
        return await message.reply(f"Error: Received status code {response.status_code} from API")

    try:
        images = response.json()
    except ValueError as e:
        return await message.reply(f"Error decoding JSON: {e}\nResponse content: {response.content}")

    media_group = []
    count = 0

    msg = await message.reply("Annie sᴄʀᴀᴘɪɴɢ ɪᴍᴀɢᴇs ғʀᴏᴍ Unsplash...")
    for result in images.get("results", [])[:6]:
        media_group.append(InputMediaPhoto(media=result["urls"]["regular"]))
        count += 1
        await msg.edit(f"=> Annie ᴏᴡᴏ sᴄʀᴀᴘᴇᴅ ɪᴍᴀɢᴇs {count}")

    try:
        await app.send_media_group(
            chat_id=chat_id,
            media=media_group,
            reply_to_message_id=message.id
        )
        return await msg.delete()
    except Exception as e:
        await msg.delete()
        return await message.reply(f"ᴇʀʀᴏʀ : {e}")
