from ANNIEMUSIC import app
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from os import environ
from typing import Union, Optional
from PIL import Image, ImageDraw, ImageFont
from os import environ
import random
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont
import asyncio, os, time, aiohttp
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from asyncio import sleep
from pyrogram import filters, Client, enums
from pyrogram.enums import ParseMode
from pyrogram import *
from pyrogram.types import *
from logging import getLogger
from ANNIEMUSIC.utils.jarvis_ban import admin_filter
import os
from PIL import ImageDraw, Image, ImageFont, ImageChops
from pyrogram import *
from pyrogram.types import *
from logging import getLogger
# --------------------------------------------------------------------------------- #

class leftDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_left(self, chat_id):
        self.data[chat_id] = {"state": "on"}  # Default state is "on"

    async def rm_left(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]

left = leftDatabase()

# --------------------------------------------------------------------------------- #

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)
resize_text = (
    lambda text_size, text: (text[:text_size] + "...").upper()
    if len(text) > text_size
    else text.upper()
)

# --------------------------------------------------------------------------------- #

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None
):
    bg = Image.open(bg_path)

    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)

    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )

    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #

bg_path = "ANNIEMUSIC/assets/userinfo.png"
font_path = "ANNIEMUSIC/assets/hiroko.ttf"

# --------------------------------------------------------------------------------- #
@app.on_message(filters.command("left") & ~filters.private)
async def auto_state(_, message):
    usage = "**Usage:**\n⦿/left [on|off]\n➤Annie left notification.........."
    if len(message.command) == 1:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    user = member.old_chat_member.user
        if member.old_chat_member
        else member.from_user
    if user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        A = await left.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        if state == "off":
            if A:
                await message.reply_text("**ʟᴇғᴛ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !**")
            else:
                await left.add_left(chat_id)
                await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ʟᴇғᴛ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ** {message.chat.title}")
        elif state == "on":
            if not A:
                await message.reply_text("**ᴇɴᴀʙʟᴇ ʟᴇғᴛ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ.**")
            else:
                await left.rm_left(chat_id)
                await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ʟᴇғᴛ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ ** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**")

# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=20)
async def member_has_left(client: app, member: ChatMemberUpdated):

    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {
            "banned", "left", "restricted"
        }
        and member.old_chat_member
    ):
        pass
    else:
        return

    user = (
        member.old_chat_member.user
        if member.old_chat_member
        else member.from_user
    )

    # Check if the user has a profile photo
    if user.photo and user.photo.big_file_id:
        try:
            # Add the photo path, caption, and button details
            photo = await app.download_media(user.photo.big_file_id)

            welcome_photo = await get_userinfo_img(
                bg_path=bg_path,
                font_path=font_path,
                user_id=user.id,
                profile_path=photo,
            )
        
            caption = f"**#New_Member_Left**\n\n**๏** {user.mention} **ʙᴀᴀᴘ ᴋᴀ ᴀᴋᴇʟᴀ ᴄʜᴏʀ ᴋᴇ ᴄʜʟᴀ ɢʏᴀ🥺**\n**๏ ᴊᴀʟᴅɪ ᴡᴀᴘᴀs ᴀᴀɴᴀ ᴍᴇʀᴀ ʙᴀᴄʜᴀ 🫠..!**"
            button_text = "๏ ᴠɪᴇᴡ ᴜsᴇʀ ๏"

            # Generate a deep link to open the user's profile
            deep_link = f"tg://openmessage?user_id={user.id}"

            # Send the message with the photo, caption, and button
            message = await client.send_photo(
                chat_id=member.chat.id,
                photo=welcome_photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, url=deep_link)]
                ])
            )

            # Schedule a task to delete the message after 300 seconds
            async def delete_message():
                await asyncio.sleep(300)
                await message.delete()

            # Run the task
            asyncio.create_task(delete_message())
            
        except RPCError as e:
            print(e)
            return
    else:
        # Handle the case where the user has no profile photo
        print(f"User {user.id} has no profile photo.")
        
