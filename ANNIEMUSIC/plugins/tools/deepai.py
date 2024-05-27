import os, time
import openai
from pyrogram import filters
from ANNIEMUSIC import app
from pyrogram.enums import ChatAction, ParseMode
from gtts import gTTS
import requests, config
import requests as r

api_key = config.DEEP_API

@app.on_message(filters.command(["uby" , ],  prefixes=["r","R"]))
async def deepchat(app: app, message):
    name = message.from_user.first_name
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(f"Hello {name}\n How can I assist you today?.")
        else:
            a = message.text.split(' ', 1)[1]

            data = {
                'text': a,  
            }

            headers = {
                'api-key': api_key,
            }

            r = requests.post("https://api.deepai.org/api/text-generator", data=data, headers=headers)
            response = r.json()
            answer_text = response['output']
            await message.reply_text(f"{answer_text}")
    except Exception as e:
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")
