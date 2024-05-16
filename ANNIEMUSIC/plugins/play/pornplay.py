import asyncio
import aiohttp
import pytgcalls
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytgcalls.types import AudioVideoPiped
from ANNIEMUSIC.plugins.play import play
from ANNIEMUSIC.plugins.play.pornplay import play
from ANNIEMUSIC import app

async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_video_info(title):
    url_base = f'https://www.xnxx.com/search/{title}'
    try:
        async with aiohttp.ClientSession() as session:
            html = await fetch_html(session, url_base)
            soup = BeautifulSoup(html, "html.parser")
            video_list = soup.findAll('div', attrs={'class': 'thumb-block'})
            if video_list:
                random_video = random.choice(video_list)
                thumbnail = random_video.find('div', class_="thumb").find('img').get("src")
                if thumbnail:
                    thumbnail_500 = thumbnail.replace('/h', '/m').replace('/1.jpg', '/3.jpg')
                    link = random_video.find('div', class_="thumb-under").find('a').get("href")
                    if link and 'https://' not in link:
                        return {'link': 'https://www.xnxx.com' + link, 'thumbnail': thumbnail_500}
    except Exception as e:
        print(f"Error: {e}")
    return None

async def get_video_stream(session, link):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    x = yt_dlp.YoutubeDL(ydl_opts)
    info = x.extract_info(link, False)
    video = os.path.join("downloads", f"{info['id']}.{info['ext']}")
    if os.path.exists(video):
        return video
    x.download([link])
    return video

@app.on_message(filter.command(["porn", "xnxx"]))
async def get_random_video_info(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide a title to search.")
        return

    title = ' '.join(message.command[1:])
    video_info = await get_video_info(title)

    if video_info:
        video_link = video_info['link']
        async with aiohttp.ClientSession() as session:
            video = await get_video_stream(session, video_link)
            vdo_link[message.chat.id] = {'link': video_link}
            keyboard1 = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⊝ ᴄʟᴏsᴇ ⊝", callback_data="close_data"), 
                    InlineKeyboardButton("⊝ ᴠᴘʟᴀʏ⊝", callback_data=f"vplay"),
                ]
            ])
            await message.reply_video(video, caption=f"{title}", reply_markup=keyboard1)
    else:
        await message.reply(f"No video link found for '{title}'.")
