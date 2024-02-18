from pyrogram import Client, filters
from pydub import AudioSegment
import io
import speech_recognition as sr
from ANNIEMUSIC import app

# Function to convert audio file to text
def audio_to_text(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio_text = recognizer.recognize_google(
            audio_data, 
            language='en-US'
        )
    return audio_text


# Command to handle /stt
@app.on_message(filters.command("stt"))
async def speech_to_text(bot, message):
    if message.reply_to_message and message.reply_to_message.audio:
        audio = message.reply_to_message.audio
        audio_data = await bot.download_media(audio)
        
        # Convert audio to WAV format
        sound = AudioSegment.from_file(io.BytesIO(audio_data))
        wav_data = io.BytesIO()
        sound.export(wav_data, format="wav")
        wav_data.seek(0)
        
        # Convert audio to text
        text = audio_to_text(wav_data)
        
        # Send the text as a reply
        await message.reply_text(text)
    else:
        await message.reply_text("Please reply to an audio file to convert it to text.")
