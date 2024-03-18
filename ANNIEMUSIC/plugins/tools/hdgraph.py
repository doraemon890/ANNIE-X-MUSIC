from telegraph import upload_file
from pyrogram import filters
import base64
import httpx
import os
from PIL import Image, ImageEnhance
from ANNIEMUSIC import app
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@app.on_message(filters.reply & filters.command(["hdtgm"]))
async def create_telegraph_link(client, message):
    try:
        if not message.reply_to_message:
            await message.reply_text("**Please reply to a message to create its Telegraph link.**")
            return

        sent_message = await message.reply_text("💻")

        if message.reply_to_message.photo:
            media = message.reply_to_message.photo
        elif message.reply_to_message.sticker:
            sticker_file_id = message.reply_to_message.sticker.file_id
            sticker_file = await client.download_media(sticker_file_id)
            # Convert sticker to image or video depending on if it's animated
            if message.reply_to_message.sticker.is_animated:
                await message.reply_to_message.download("animated_sticker.webp")
                await convert_animated_sticker_to_video("animated_sticker.webp", "animated_sticker.mp4")
                media = "animated_sticker.mp4"
            else:
                sticker_image = Image.open(sticker_file)
                sticker_image.save("sticker_as_image.png")
                media = "sticker_as_image.png"
        else:
            await message.reply_text("**Unsupported media type. Please reply to an image or a sticker.**")
            return

        # Increase brightness
        if isinstance(media, str):  # Check if media is an image or video file path
            if media.endswith(".mp4"):
                brightened_video_path = await increase_brightness_video(media)
                telegraph_url = upload_file(brightened_video_path)[0]
            else:
                image = Image.open(media)
                enhancer = ImageEnhance.Brightness(image)
                brightened_image = enhancer.enhance(1.1)  # Increase brightness by 50%
                # Save the brightened image
                brightened_file_path = "brightened_image.png"
                brightened_image.save(brightened_file_path)
                telegraph_url = upload_file(brightened_file_path)[0]
        else:  # Media is a photo object
            image = Image.open(await client.download_media(media))
            enhancer = ImageEnhance.Brightness(image)
            brightened_image = enhancer.enhance(1.1)  # Increase brightness by 50%
            # Save the brightened image
            brightened_file_path = "brightened_image.png"
            brightened_image.save(brightened_file_path)
            telegraph_url = upload_file(brightened_file_path)[0]

        # Create caption with the Telegraph link as a button
        button_text = "Open in Telegraph"
        button_url = "https://telegra.ph" + telegraph_url
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(button_text, url=button_url)]]
        )

        await client.send_photo(
            message.chat.id,
            photo=brightened_file_path,
            caption=f"**Here is your Telegraph link with increased brightness:**\n\n{button_url}\n\n**Made by @{app.username}**",
            reply_markup=reply_markup,
        )

        # Delete the "Processing..." message after sending the results
        await sent_message.delete()

    except Exception as e:
        print(f"Failed to create Telegraph link: {e}")
        await message.reply_text("**Failed to create Telegraph link. Please try again later.**")

async def convert_animated_sticker_to_video(input_file, output_file):
    command = f"ffmpeg -i {input_file} -vf 'fps=25,scale=320:-1:flags=lanczos' -c:v libx264 -crf 20 -pix_fmt yuv420p {output_file}"
    os.system(command)

async def increase_brightness_video(video_path):
    brightened_video_path = "brightened_video.mp4"
    command = f"ffmpeg -i {video_path} -vf 'eq=brightness=0.5' -c:a copy {brightened_video_path}"
    os.system(command)
    return brightened_video_path
