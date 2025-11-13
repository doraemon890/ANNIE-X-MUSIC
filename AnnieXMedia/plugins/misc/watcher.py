from pyrogram import filters
from pyrogram.types import Message

from AnnieXMedia import app
from AnnieXMedia.core.call import StreamController 

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await StreamController .force_stop_stream(message.chat.id)
