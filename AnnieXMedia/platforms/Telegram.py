import asyncio
import os
import time
from typing import Optional, Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from AnnieXMedia import app
from AnnieXMedia.utils.formatters import (
    check_duration,
    convert_bytes,
    get_readable_time,
    seconds_to_min,
)


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = 5

    async def send_split_text(self, message, string: str) -> bool:
        n = self.chars_limit
        out = [string[i : i + n] for i in range(0, len(string), n)]
        for j, x in enumerate(out[:3], 1):
            await message.reply_text(x, disable_web_page_preview=True)
        return True

    async def get_link(self, message):
        return message.link

    async def get_filename(self, file, audio: Union[bool, str] = None) -> str:
        try:
            file_name = getattr(file, "file_name", None)
            if not file_name:
                file_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        except Exception:
            file_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        return file_name

    async def get_duration(self, file_obj, file_path: Optional[str] = None) -> str:
        try:
            if hasattr(file_obj, "duration") and file_obj.duration:
                return seconds_to_min(file_obj.duration)
        except Exception:
            pass

        if file_path:
            try:
                dur = await asyncio.get_event_loop().run_in_executor(
                    None, check_duration, file_path
                )
                return seconds_to_min(dur)
            except Exception:
                pass

        return "Unknown"

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ) -> str:
        base = os.path.realpath("downloads")
        if audio:
            try:
                ext = (audio.file_name.split(".")[-1]) if not isinstance(audio, Voice) else "ogg"
            except Exception:
                ext = "ogg"
            file_name = f"{audio.file_unique_id}.{ext}"
            return os.path.join(base, file_name)
        if video:
            try:
                ext = video.file_name.split(".")[-1]
            except Exception:
                ext = "mp4"
            file_name = f"{video.file_unique_id}.{ext}"
            return os.path.join(base, file_name)
        return os.path.join(base, f"{int(time.time())}.dat")

    async def download(self, _, message, mystic, fname: str) -> bool:
        lower = [0, 8, 17, 38, 64, 77, 96]
        higher = [5, 10, 20, 40, 66, 80, 99]
        checker = [5, 10, 20, 40, 66, 80, 99]
        speed_counter = {}

        if os.path.exists(fname):
            return True

        async def down_load():
            async def progress(current, total):
                if current == total or total == 0:
                    return
                if message.id not in speed_counter:
                    speed_counter[message.id] = time.time()
                elapsed = max(time.time() - speed_counter[message.id], 1e-3)

                upl = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="stop_downloading")]]
                )

                percentage = current * 100 / total
                try:
                    speed = current / elapsed
                    eta_s = int((total - current) / max(speed, 1e-6))
                except Exception:
                    speed, eta_s = 0, 0

                eta = get_readable_time(eta_s) or "0 sᴇᴄᴏɴᴅs"
                total_size = convert_bytes(total)
                completed_size = convert_bytes(current)
                speed_h = convert_bytes(speed)
                percentage_i = int(percentage)

                for counter in range(7):
                    low, high, check = int(lower[counter]), int(higher[counter]), int(checker[counter])
                    if low < percentage_i <= high and high == check:
                        try:
                            await mystic.edit_text(
                                text=_["tg_1"].format(
                                    app.mention, total_size, completed_size, str(percentage)[:5], speed_h, eta
                                ),
                                reply_markup=upl,
                            )
                            checker[counter] = 100
                        except Exception:
                            pass

            speed_counter[message.id] = time.time()
            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                try:
                    elapsed = get_readable_time(int(time.time() - speed_counter[message.id]))
                except Exception:
                    elapsed = "0 sᴇᴄᴏɴᴅs"
                await mystic.edit_text(_["tg_2"].format(elapsed))
            except Exception:
                await mystic.edit_text(_["tg_3"])

        task = asyncio.create_task(down_load())
        config.lyrical[mystic.id] = task
        await task
        verify = config.lyrical.get(mystic.id)
        if not verify:
            return False
        config.lyrical.pop(mystic.id, None)
        return True
