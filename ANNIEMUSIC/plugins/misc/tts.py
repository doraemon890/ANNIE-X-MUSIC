from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ANNIEMUSIC import app
import pyttsx3
import os

@app.on_message(filters.command('tts'))
def text_to_speech(client, message):
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
        client.send_message(message.chat.id, "Select voice:", reply_markup=reply_markup)

@app.on_callback_query()
def voice_selection(client, callback_query):
    text = callback_query.message.text
    voice = callback_query.data
    
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
    client.send_audio(callback_query.message.chat.id, speech_file)
    
    # Remove temporary file
    os.remove(speech_file)
