import os
import time
from gtts import gTTS
import openai
import requests
from pyrogram import filters
from pyrogram.enums import ChatAction, ParseMode
from ANNIEMUSIC import app
import config
from config import GPT_API

# Set up OpenAI API
openai.api_key = config.GPT_API

# Define API URL for search
API_URL = "https://sugoi-api.vercel.app/search"

# Command for GPT chat
@app.on_message(filters.command(["chatgpt", "ai", "ask", "Master"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def chat_gpt(app, message):
    try:
        # Start typing action
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            # Reply with default message if no query provided
            await message.reply_text("**Hello sir, I am Jarvis. How can I help you today?**")
        else:
            query = message.text.split(' ', 1)[1]
            MODEL = "gpt-3.5-turbo"
            # Generate response using OpenAI GPT
            resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role": "user", "content": query}],
                                                 temperature=0.2)
            response_text = resp['choices'][0]["message"]["content"]
            await message.reply_text(response_text)
    except Exception as e:
        await message.reply_text(f"**Error**: {e}")

# Command for GPT chat with user's name
@app.on_message(filters.command(["arvis"], prefixes=["j", "J"]))
async def chat_arvis(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name
        if len(message.command) < 2:
            await message.reply_text(f"**Hello {name}, I am Jarvis. How can I help you today?**")
        else:
            query = message.text.split(' ', 1)[1]
            MODEL = "gpt-3.5-turbo"
            resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role": "user", "content": query}],
                                                 temperature=0.2)
            response_text = resp['choices'][0]["message"]["content"]
            await message.reply_text(response_text)
    except Exception as e:
        await message.reply_text(f"**Error**: {e}")

# Command for ANNIE with user's name
@app.on_message(filters.command(["iri"], prefixes=["s", "S"]))
async def chat_annie(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name
        if len(message.command) < 2:
            await message.reply_text(f"**Hello {name}, I am ANNIE. How can I help you today?**")
        else:
            query = message.text.split(' ', 1)[1]
            MODEL = "gpt-3.5-turbo"
            resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role": "user", "content": query}],
                                                 temperature=0.2)
            response_text = resp['choices'][0]["message"]["content"]
            tts = gTTS(response_text, lang='en')
            tts.save('output.mp3')
            await app.send_voice(chat_id=message.chat.id, voice='output.mp3')
            os.remove('output.mp3')
    except Exception as e:
        await message.reply_text(f"**Error**: {e}")

# Command for Bing search
@app.on_message(filters.command(["bing"], prefixes=["+", ".", "/", "-", "?", "$", "#", "&"]))
async def bing_search(app, message):
    try:
        if len(message.command) == 1:
            await message.reply_text("Please provide a keyword to search.")
            return

        keyword = " ".join(message.command[1:])
        params = {"keyword": keyword}
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            results = response.json()
            if not results:
                await message.reply_text("No results found.")
            else:
                message_text = ""
                for result in results[:7]:
                    title = result.get("title", "")
                    link = result.get("link", "")
                    message_text += f"{title}\n{link}\n\n"
                await message.reply_text(message_text.strip())
        else:
            await message.reply_text("Sorry, something went wrong with the search.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")