import openai
import aiohttp
import base64
import os
import requests
from pyrogram import filters
from config import BOT_USERNAME, GPT_API  # Importing GPT_API directly
from ANNIEMUSIC import app
from uuid import uuid4
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Set up OpenAI API
openai.api_key = GPT_API  # Using GPT_API directly

# Upscale image functionality
@app.on_message(filters.reply & filters.command("upscale"))
async def upscale_image_command_handler(_, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("**Please reply to an image to upscale it.**")
            return

        image = await app.download_media(message.reply_to_message.photo.file_id)

        # Encode image bytes to base64
        with open(image, "rb") as image_file:
            image_bytes = image_file.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # Upscale image using DALL-E-3 model
        response = openai.Image.create(
            image={"image": encoded_image},  # Pass image data as dictionary
            model="text-dalle-3"
        )

        # Get upscaled image URL
        upscaled_image_url = response.url

        # Send the upscaled image
        await app.send_photo(
            message.chat.id,
            photo=upscaled_image_url,
            caption="**Here is the upscaled image!**"
        )

    except Exception as e:
        print(f"Failed to upscale the image: {e}")
        await message.reply_text("**Failed to upscale the image. Please try again later.**")

# Waifu image functionality
@app.on_message(filters.command("waifu"))
async def waifu_command_handler(_, message):
    try:
        tags = ['maid']  # You can customize the tags as needed
        waifu_data = get_waifu_data(tags)

        if waifu_data and 'images' in waifu_data:
            first_image = waifu_data['images'][0]
            image_url = first_image['url']
            await message.reply_photo(image_url)
        else:
            await message.reply_text("No waifu found with the specified tags.")

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply_text(f"An error occurred: {e}")

# Helper function to get waifu data
def get_waifu_data(tags):
    params = {
        'included_tags': tags,
        'height': '>=2000'
    }

    response = requests.get('https://api.waifu.im/search', params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None
