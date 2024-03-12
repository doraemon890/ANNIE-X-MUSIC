from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import app
import pyttsx3
import os


@app.on_message(filters.command('tts'))
async def text_to_speech(client, message):
    # Check if text exists after the command
    if len(message.text.split(' ', 1)) > 1:
        text = message.text.split(' ', 1)[1]
        
        # Create inline keyboard for voice selection
        keyboard = [
            [InlineKeyboardButton("Robot Voice", callback_data='robot')],
            [InlineKeyboardButton("Girl Voice", callback_data='girl')],
            [InlineKeyboardButton("Man Voice", callback_data='man')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send message with voice selection buttons
        await message.reply_text("Select voice:", reply_markup=reply_markup)

@app.on_callback_query()
async def voice_selection(client, callback_query):
    # Extract relevant information from callback query
    voice = callback_query.data
    text = callback_query.message.reply_to_message.text
    
    # Initialize engine
    engine = pyttsx3.init()
    
    # Set voice based on user selection
    if voice == 'robot':
        engine.setProperty('voice', 'english_rp+f4')
    elif voice == 'girl':
        engine.setProperty('voice', 'english+f3')
    elif voice == 'man':
        engine.setProperty('voice', 'english+m3')
    
    # Generate speech and send
    speech_file = f'speech_{voice}.mp3'
    engine.save_to_file(text, speech_file)
    engine.stop()
    engine.runAndWait()
    
    # Send the file
    await callback_query.message.reply_audio(audio=speech_file)
    
    # Remove temporary file
    os.remove(speech_file)
