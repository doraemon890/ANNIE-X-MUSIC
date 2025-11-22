# Authored By Certified Coders © 2025
import asyncio

import speedtest
from pyrogram import filters
from pyrogram.types import Message

from AnnieXMedia import app
from AnnieXMedia.misc import SUDOERS
from AnnieXMedia.utils.decorators.language import language


def run_speedtest():
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    return test.results.dict()


@app.on_message(filters.command(["speedtest", "spt"]) & SUDOERS)
@language
async def speedtest_function(_, message: Message, lang):
    try:
        m = await message.reply_text(lang["server_11"])
        await m.edit_text(lang["server_12"])

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_speedtest)

        await m.edit_text(lang["server_13"])  #

        output = lang["server_15"].format(
            result["client"]["isp"],
            result["client"]["country"],
            result["server"]["name"],
            result["server"]["country"],
            result["server"]["cc"],
            result["server"]["sponsor"],
            result["server"]["latency"],
            result["ping"],
        )

        await m.edit_text(lang["server_14"])
        await message.reply_photo(photo=result["share"], caption=output)
        await m.delete()

    except Exception as e:
        await message.reply_text(f"<code>{e}</code>")
