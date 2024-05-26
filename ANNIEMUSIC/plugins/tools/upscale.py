import os
import config
from config import BOT_USERNAME
from ANNIEMUSIC import app
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiofiles
import aiohttp
import requests

async def load_image(image_path: str, url: str) -> str:
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(image_path, mode="wb") as file:
                    await file.write(await response.read())
                return image_path
            return None

@app.on_message(filters.command("upscale", prefixes="/"))
async def upscale_image(client, message):
    chat_id = message.chat.id
    replied_message = message.reply_to_message
    
    if not config.DEEP_API:
        return await message.reply_text("I can't upscale without a DEEP API key!")
    
    if not replied_message or not replied_message.photo:
        return await message.reply_text("Please reply to an image.")
    
    aux_message = await message.reply_text("Upscaling, please wait...")
    image_path = await replied_message.download()
    
    response = requests.post(
        "https://api.deepai.org/api/torch-srgan",
        files={'image': open(image_path, 'rb')},
        headers={'api-key': config.DEEP_API}
    ).json()
    
    image_url = response.get("output_url")
    if not image_url:
        return await aux_message.edit("Failed to upscale image, please try again.")
    
    downloaded_image = await load_image(image_path, image_url)
    if not downloaded_image:
        return await aux_message.edit("Failed to download upscaled image, please try again.")
    
    await aux_message.delete()
    await message.reply_photo(photo=downloaded_image)

@app.on_message(filters.command("getdraw", prefixes="/"))
async def draw_image(client, message):
    chat_id = message.chat.id
    user_id = message.sender_chat.id if message.sender_chat else message.from_user.id
    replied_message = message.reply_to_message
    
    if not config.DEEP_API:
        return await message.reply_text("I can't generate images without a DEEP API key!")
    
    if replied_message and replied_message.text:
        query = replied_message.text
    elif len(message.text.split()) > 1:
        query = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("Please provide text or reply to a text message.")
    
    aux_message = await message.reply_text("Generating image, please wait...")
    image_path = f"cache/{user_id}_{chat_id}_{message.id}.png"
    
    response = requests.post(
        "https://api.deepai.org/api/text2img",
        data={'text': query, 'grid_size': '1', 'image_generator_version': 'hd'},
        headers={'api-key': config.DEEP_API}
    ).json()
    
    image_url = response.get("output_url")
    if not image_url:
        return await aux_message.edit("Failed to generate image, please try again.")
    
    downloaded_image = await load_image(image_path, image_url)
    if not downloaded_image:
        return await aux_message.edit("Failed to download generated image, please try again.")
    
    await aux_message.delete()
    await message.reply_photo(photo=downloaded_image, caption=query)
