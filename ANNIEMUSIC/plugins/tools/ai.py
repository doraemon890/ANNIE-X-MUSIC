import asyncio
import base64
import mimetypes
import os
from pyrogram import filters, types as t
from lexica import AsyncClient
from ANNIEMUSIC import app
from lexica.constants import languageModels


async def chat_completion(prompt, model) -> tuple | str:
    try:
        model_info = getattr(languageModels, model)
        client = AsyncClient()
        output = await client.ChatCompletion(prompt, model_info)
        if model == "bard":
            return output['content'], output['images']
        return output['content']
    except Exception as e:
        raise Exception(f"API error: {e}")


async def gemini_vision(prompt, model, images) -> tuple | str:
    image_info = []
    for image in images:
        with open(image, "rb") as image_file:
            data = base64.b64encode(image_file.read()).decode("utf-8")
            mime_type, _ = mimetypes.guess_type(image)
            image_info.append({
                "data": data,
                "mime_type": mime_type
            })
        os.remove(image)
    payload = {
        "images": image_info
    }
    model_info = getattr(languageModels, model)
    client = AsyncClient()
    output = await client.ChatCompletion(prompt, model_info, json=payload)
    return output['content']['parts'][0]['text']


def get_media(message):
    """Extract Media"""
    media = None
    if message.media:
        if message.photo:
            media = message.photo
        elif message.document and message.document.mime_type in ['image/png', 'image/jpg', 'image/jpeg'] \
                and message.document.file_size < 5242880:
            media = message.document
    elif message.reply_to_message and message.reply_to_message.media:
        if message.reply_to_message.photo:
            media = message.reply_to_message.photo
        elif message.reply_to_message.document and message.reply_to_message.document.mime_type in ['image/png',
                                                                                                      'image/jpg',
                                                                                                      'image/jpeg'] \
                and message.reply_to_message.document.file_size < 5242880:
            media = message.reply_to_message.document
    return media


def get_text(message):
    """Extract Text From Commands"""
    if message.text is None:
        return None
    if " " in message.text:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@app.on_message(filters.command(["bard", "gpt", "llama", "mistral", "palm", "gemini"]))
async def chat_bots(_, m: t.Message):
    prompt = get_text(m)
    media = get_media(m)
    if media is not None:
        return await ask_about_image(_, m, [media], prompt)
    if prompt is None:
        return await m.reply_text("Hello, how can I assist you today?")
    model = m.command[0].lower()
    output = await chat_completion(prompt, model)
    if model == "bard":
        output, images = output
        if len(images) == 0:
            return await m.reply_text(output)
        media = [t.InputMediaPhoto(i) for i in images]
        media[0] = t.InputMediaPhoto(images[0], caption=output)
        await _.send_media_group(
            m.chat.id,
            media,
            reply_to_message_id=m.message_id
        )
    else:
        await m.reply_text(output['parts'][0]['text'] if model == "gemini" else output)


async def ask_about_image(_, m: t.Message, media_files: list, prompt: str):
    images = []
    for media in media_files:
        image = await _.download_media(media.file_id, file_name=f'./downloads/{m.from_user.id}_ask.jpg')
        images.append(image)
    output = await gemini_vision(prompt if prompt else "What's this?", "geminiVision", images)
    await m.reply_text(output)