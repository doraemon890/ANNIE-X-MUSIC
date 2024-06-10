import json
import aiohttp
import requests
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message
from ANNIEMUSIC import app

UNSPLASH_API_KEY = 'UwPT7-Of5XQgwxHx-GfcXa4sK0O_38Pbi-6FrQ5f7AY'

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP request failed with status code {response.status} for URL: {url}")
            return await response.text()

@app.on_message(filters.command("img"))
async def bingimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("🔎")

    bingimg_url = "https://sugoi-api.vercel.app/bingimg?keyword=" + text
    try:
        resp_text = await fetch(bingimg_url)
        images = json.loads(resp_text)
    except Exception as e:
        await message.reply_text(f"Error fetching images: {str(e)}")
        await search_message.delete()
        return

    media = [InputMediaPhoto(media=img) for img in images[:7]]

    await message.reply_media_group(media=media)
    await search_message.delete()
    await message.delete()

@app.on_message(filters.command(["image"], prefixes=["/", "!"]))
async def pinterest(_, message: Message):
    chat_id = message.chat.id

    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("ɢɪᴠᴇ ɪᴍᴀɢᴇ ɴᴀᴍᴇ ғᴏʀ sᴇᴀʀᴄʜ 🔍")

    response = requests.get(f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_API_KEY}")

    if response.status_code != 200:
        return await message.reply(f"Error: Received status code {response.status_code} from API")

    try:
        images = response.json()
    except ValueError as e:
        return await message.reply(f"Error decoding JSON: {e}\nResponse content: {response.content}")

    media_group = []
    count = 0

    msg = await message.reply("Annie sᴄʀᴀᴘɪɴɢ ɪᴍᴀɢᴇs...")
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
