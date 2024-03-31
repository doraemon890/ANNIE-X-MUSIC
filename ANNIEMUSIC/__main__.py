import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ANNIEMUSIC import LOGGER, app, userbot
from ANNIEMUSIC.core.call import JARVIS
from ANNIEMUSIC.misc import sudo
from ANNIEMUSIC.plugins import ALL_MODULES
from ANNIEMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ sᴇssɪᴏɴ ɴᴏᴛ ғɪʟʟᴇᴅ, ᴘʟᴇᴀsᴇ ғɪʟʟ ᴀ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ANNIEMUSIC.plugins" + all_module)
    LOGGER("ANNIEMUSIC.plugins").info("ᴀɴɴɪᴇ's ᴍᴏᴅᴜʟᴇs ʟᴏᴀᴅᴇᴅ...")
    await userbot.start()
    await JARVIS.start()
    try:
        await JARVIS.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ANNIEMUSIC").error(
            "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ.\n\nᴀɴɴɪᴇ ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ..."
        )
        exit()
    except:
        pass
    await JARVIS.decorators()
    LOGGER("ANNIEMUSIC").info(
        "\x41\x6e\x6e\x69\x65\x20\x4d\x75\x73\x69\x63\x20\x52\x6f\x62\x6f\x74\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x2e\x2e"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ANNIEMUSIC").info("sᴛᴏᴘɪɴɢ ᴀɴɴɪᴇ ᴍᴜsɪᴄ ʙᴏᴛ ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
