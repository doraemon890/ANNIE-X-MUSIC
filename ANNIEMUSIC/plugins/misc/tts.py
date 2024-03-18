import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import app
# Your Play.ht API key
PLAYHT_API_KEY = '53be44590ea344e3906e212e3d38835e'



# Function to convert text to speech using Play.ht API
def text_to_speech(text, voice):
    url = "https://play.ht/api/tts"
    headers = {
        "Authorization": f"Bearer {PLAYHT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "voice": voice,
        "text": text
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['audio_url']
    else:
        return None

# Handler to process /start command
@app.on_message(filters.command("voice"))
def start(client, message):
    message.reply_text("Welcome! Select a voice model to convert text to speech:")
    
    # Create inline keyboard with voice models
    voices = [
        "Joanna",
        "Matthew",
        "Ivy",
        "Brian",
        "Emma",
        "Justin",
        "Kendra",
        "Kimberly",
        "Salli",
        "Joey"
    ]
    buttons = [
        [InlineKeyboardButton(voice, callback_data=voice)] for voice in voices
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    message.reply_text("Select a voice model:", reply_markup=reply_markup)

# Handler to process inline button clicks
@app.on_callback_query()
def callback(client, callback_query):
    voice = callback_query.data
    message = callback_query.message
    message.reply_text("Processing...")
    
    audio_url = text_to_speech("Hello, this is a test message.", voice)
    if audio_url:
        message.reply_voice(audio_url)
    else:
        message.reply_text("Failed to convert text to speech.")
