import httpx
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from AnnieXMedia import app

timeout = httpx.Timeout(40.0)
http = httpx.AsyncClient(http2=True, timeout=timeout)

weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"
get_coords_url = "https://api.weather.com/v3/location/search"
weather_data_url = "https://api.weather.com/v3/aggcommon/v3-wx-observations-current"

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2012K11AG Build/SQ1D.211205.017)"
}


@app.on_message(filters.command("weather"))
async def weather_command(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text(
            "<b>ᴜsᴀɢᴇ:</b> <code>/weather city</code>\nExample: <code>/weather delhi</code>",
            parse_mode=enums.ParseMode.HTML
        )

    query = message.text.split(maxsplit=1)[1]

    try:
        coord_response = await http.get(
            get_coords_url,
            headers=headers,
            params={
                "apiKey": weather_apikey,
                "format": "json",
                "language": "en",
                "query": query
            },
        )
        coord_data = coord_response.json()

        if not coord_data.get("location"):
            return await message.reply_text(
                "❌ <b>Location not found.</b> Please try a different city.",
                parse_mode=enums.ParseMode.HTML
            )

        latitude = coord_data["location"]["latitude"][0]
        longitude = coord_data["location"]["longitude"][0]
        location_name = coord_data["location"]["address"][0]

        weather_response = await http.get(
            weather_data_url,
            headers=headers,
            params={
                "apiKey": weather_apikey,
                "format": "json",
                "language": "en",
                "geocode": f"{latitude},{longitude}",
                "units": "m"
            },
        )
        weather_data = weather_response.json()
        obs = weather_data.get("v3-wx-observations-current", {})

        if not obs:
            return await message.reply_text(
                "⚠️ <b>Weather data not available</b> at the moment.",
                parse_mode=enums.ParseMode.HTML
            )

        weather_text = (
            f"<b>{location_name}</b> 🌍\n\n"
            f"🌡️ <b>ᴛᴇᴍᴘᴇʀᴀᴛᴜʀᴇ:</b> <code>{obs.get('temperature', 'N/A')} °C</code>\n"
            f"🥵 <b>ғᴇᴇʟs ʟɪᴋᴇ:</b> <code>{obs.get('temperatureFeelsLike', 'N/A')} °C</code>\n"
            f"💧 <b>ʜᴜᴍɪᴅɪᴛʏ:</b> <code>{obs.get('relativeHumidity', 'N/A')}%</code>\n"
            f"💨 <b>ᴡɪɴᴅ:</b> <code>{obs.get('windSpeed', 'N/A')} km/h</code>\n"
            f"☁️ <b>ᴄᴏɴᴅɪᴛɪᴏɴ:</b> <i>{obs.get('wxPhraseLong', 'N/A')}</i>"
        )

        await message.reply_text(weather_text, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        print(f"Error in /weather: {e}")
        await message.reply_text(
            "❌ <b>An error occurred</b> while fetching the weather. Please try again later.",
            parse_mode=enums.ParseMode.HTML
        )
