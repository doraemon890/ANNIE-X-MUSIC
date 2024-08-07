import asyncio
import os
import re
from typing import Union
from googleapiclient.discovery import build
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from config import YTAPI
from ANNIEMUSIC.utils.database import is_on_off
from ANNIEMUSIC.utils.formatters import time_to_seconds
import yt_dlp

# Initialize YouTube Data API client
YOUTUBE_API_KEY = YTAPI  # Assuming you have the correct key in config
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            return bool(response['items'])
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset: offset + length]

    def extract_video_id(self, link: str) -> Union[str, None]:
        match = re.search(r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/)|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?v=|youtube\.com\/watch\?v%3D|youtube\.com\/watch\?v=|youtube\.com\/watch\?v%3D|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})', link)
        return match.group(1) if match else None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            )
            response = request.execute()
            video = response['items'][0]
            title = video['snippet']['title']
            duration = video['contentDetails']['duration']
            thumbnail = video['snippet']['thumbnails']['high']['url']
            duration_sec = int(time_to_seconds(duration))
            return title, duration, duration_sec, thumbnail, video_id
        return None, None, None, None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            return response['items'][0]['snippet']['title']
        return None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='contentDetails',
                id=video_id
            )
            response = request.execute()
            return response['items'][0]['contentDetails']['duration']
        return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            return response['items'][0]['snippet']['thumbnails']['high']['url']
        return None

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        playlist_id = link.split('list=')[-1]
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=limit
        )
        response = request.execute()
        video_ids = [item['snippet']['resourceId']['videoId'] for item in response['items']]
        return video_ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        video_id = self.extract_video_id(link)
        if video_id:
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            video = response['items'][0]
            title = video['snippet']['title']
            thumbnail = video['snippet']['thumbnails']['high']['url']
            yturl = link
            track_details = {
                "title": title,
                "link": yturl,
                "vidid": video_id,
                "thumbnail": thumbnail,
            }
            return track_details, video_id
        return None, None

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        # YouTube Data API does not provide format details. Use yt-dlp or another tool for this.
        return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        # Use the search API to get multiple results
        if videoid:
            link = self.base + link
        search_query = link.split('v=')[-1]
        request = youtube.search().list(
            part='snippet',
            q=search_query,
            type='video',
            maxResults=10
        )
        response = request.execute()
        result = response['items']
        if query_type < len(result):
            video = result[query_type]
            title = video['snippet']['title']
            duration = video['snippet'].get('duration', 'Unknown')
            vidid = video['id']['videoId']
            thumbnail = video['snippet']['thumbnails']['high']['url']
            return title, duration, thumbnail, vidid
        return None, None, None, None

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def audio_dl():
            # Handle audio download using yt-dlp
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, download=True)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            return xyz

        def video_dl():
            # Handle video download using yt-dlp
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, download=True)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            return xyz

        def song_video_dl():
            # Handle video download with audio using yt-dlp
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_opts = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            x.download([link])

        def song_audio_dl():
            # Handle audio download with specific format using yt-dlp
            fpath = f"downloads/{title}.%(ext)s"
            ydl_opts = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            x.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            return fpath
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath
        elif video:
            if await is_on_off(1):
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    f"{link}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = None
                else:
                    return
        else:
            direct = True
            downloaded_file = await loop.run_in_executor(None, audio_dl)
        return downloaded_file, direct
