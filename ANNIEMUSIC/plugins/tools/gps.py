import asyncio
from requests import get
from pyrogram import enums, filters, idle
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from pyrogram.handlers import MessageHandler
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from ANNIEMUSIC import app

@app.on_message(filters.command(["gps"]))
async def gps(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("Example:\n\n/gps [latitude, longitude]")
    
    coordinates = message.text.split(' ')[1].split(',')
    try:
        geolocator = Nominatim(user_agent="legend-jarvis")
        location = geolocator.reverse(coordinates, addressdetails=True, zoom=18)
        address = location.raw['address']

        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        latitude = location.latitude
        longitude = location.longitude


        url = [[IKB("View it", url=f"https://www.google.com/maps/search/{latitude},{longitude}")]]

        url = [[IKB("Open with:🌏ɢᴏᴏɢʟᴇ ᴍᴀᴘs", url=f"https://www.google.com/maps/search/{latitude},{longitude}")]]

        
        await message.reply_venue(latitude, longitude, f"{city}", f"{state}, {country}", reply_markup=IKM(url))
    except Exception as e:
        await message.reply_text(f"I can't find that \nDue to {e}")

@app.on_message(filters.command(["distance"]))
async def distance(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("Example:\n\n/distance [latitude, longitude],[latitude, longitude]")

    try:
        points = message.text.split(" ")[1].split(',')
        x = points[0:2]
        y = points[2:4]
        dist = great_circle(x, y).miles

        await message.reply_text(f"Total distance between {x[0]},{x[1]} and {y[0]},{y[1]} is {dist} miles")
    except Exception as e:
        await message.reply_text(f"I can't find that \nDue to {e}")
