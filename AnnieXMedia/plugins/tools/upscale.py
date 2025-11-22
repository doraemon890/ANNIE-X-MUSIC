# Authored By Certified Coders © 2025
import os
import aiohttp
import aiofiles

from config import DEEP_API
from AnnieXMedia import app
from pyrogram import filters
from pyrogram.types import Message


async def download_from_url(path: str, url: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(path, mode="wb") as f:
                    await f.write(await resp.read())
                return path
    return None


async def post_file(url: str, file_path: str, headers: dict):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('image', f, filename=os.path.basename(file_path), content_type='application/octet-stream')

            async with session.post(url, data=form, headers=headers) as resp:
                return await resp.json()


async def post_data(url: str, data: dict, headers: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            return await resp.json()


@app.on_message(filters.command("upscale"))
async def upscale_image(_, message: Message):
    if not DEEP_API:
        return await message.reply_text("🚫 Missing DeepAI API key.")

    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.reply_text("📎 Please reply to an image.")

    status = await message.reply_text("🔄 Upscaling image...")

    try:
        local_path = await reply.download()
        resp = await post_file(
            "https://api.deepai.org/api/torch-srgan",
            local_path,
            headers={'api-key': DEEP_API}
        )

        image_url = resp.get("output_url")
        if not image_url:
            return await status.edit("❌ Upscale request failed.")

        final_path = await download_from_url(local_path, image_url)
        if not final_path:
            return await status.edit("❌ Could not download result.")

        await status.delete()
        await message.reply_document(final_path)

    except Exception as e:
        await status.edit(f"⚠️ Error: `{str(e)}`")


@app.on_message(filters.command("getdraw"))
async def draw_image(_, message: Message):
    if not DEEP_API:
        return await message.reply_text("🚫 DeepAI API key is missing.")

    reply = message.reply_to_message
    query = None

    if reply and reply.text:
        query = reply.text
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]

    if not query:
        return await message.reply_text("💬 Please reply or provide text.")

    status = await message.reply_text("🎨 Generating image...")

    user_id = message.from_user.id
    chat_id = message.chat.id
    temp_path = f"cache/{user_id}_{chat_id}_{message.id}.png"

    try:
        resp = await post_data(
            "https://api.deepai.org/api/text2img",
            data={'text': query, 'grid_size': '1', 'image_generator_version': 'hd'},
            headers={'api-key': DEEP_API}
        )

        image_url = resp.get("output_url")
        if not image_url:
            return await status.edit("❌ Failed to generate image.")

        final_path = await download_from_url(temp_path, image_url)
        if not final_path:
            return await status.edit("❌ Error downloading image.")

        await status.delete()
        await message.reply_photo(final_path, caption=f"`{query}`")

    except Exception as e:
        await status.edit(f"⚠️ Error: `{str(e)}`")
