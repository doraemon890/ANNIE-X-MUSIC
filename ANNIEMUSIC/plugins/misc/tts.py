from pyrogram import Client, filters
from gtts import gTTS
import speech_recognition as sr
from ANNIEMUSIC import app

@app.on_message(filters.command('tts'))
def text_to_speech(client, message):
    if len(message.text.split(' ', 1)) > 1:
        text = message.text.split(' ', 1)[1]
        tts = gTTS(text=text, lang='hi')
        tts.save('speech.mp3')
        client.send_audio(message.chat.id, 'speech.mp3')

@app.on_message(filters.command('stt'))
def speech_to_text(client, message):
    if message.voice:
        voice_file = client.download_media(message.voice)
        recognizer = sr.Recognizer()
        with sr.AudioFile(voice_file) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                client.send_message(message.chat.id, text)
            except sr.UnknownValueError:
                client.send_message(message.chat.id, "Sorry, I couldn't understand the audio.")
            except sr.RequestError as e:
                client.send_message(message.chat.id, f"Sorry, an error occurred: {e}")
    else:
        client.send_message(message.chat.id, "Please send a voice message for speech-to-text conversion.")
