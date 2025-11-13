import os
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pydub import AudioSegment
from AnnieXMedia import app

MAX_SIZE_MB = 50
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


@app.on_message(filters.command("extract") & filters.reply)
async def extract_media(_, message: Message):
    replied = message.reply_to_message

    if not (replied and replied.video):
        return await message.reply_text("❌ Please reply to a *video* message.")
    if len(message.command) < 2:
        return await message.reply_text("ℹ️ Use `/extract audio` or `/extract video`.", quote=True)

    if replied.video.file_size > MAX_SIZE_BYTES:
        return await message.reply_text(
            f"🚫 File is too large ({replied.video.file_size // (1024*1024)} MB).\n"
            f"Maximum allowed size is {MAX_SIZE_MB} MB."
        )

    command = message.command[1].lower()
    processing_msg = await message.reply_text("🔧 Processing video…")

    file_path = None
    try:
        file_path = await replied.download(file_name="media_input.mp4")

        if command == "audio":
            output_audio = "output_audio.mp3"

            def process_audio():
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_channels(1)
                audio.export(output_audio, format="mp3")

            await asyncio.to_thread(process_audio)
            await app.send_audio(message.chat.id, output_audio, caption="🎧 Audio extracted.")
            os.remove(output_audio)

        elif command == "video":
            output_video = "output_video.mp4"

            def process_video():
                os.system(f"ffmpeg -hide_banner -loglevel error -i '{file_path}' -c copy -an '{output_video}'")

            await asyncio.to_thread(process_video)
            await app.send_video(message.chat.id, output_video, caption="🎞️ Video with no audio.")
            os.remove(output_video)

        else:
            return await message.reply_text("❌ Invalid command. Use `/extract audio` or `/extract video`.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

    finally:
        await processing_msg.delete()
        if file_path and os.path.exists(file_path):
            os.remove(file_path)