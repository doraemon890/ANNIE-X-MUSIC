import os
import requests
from random import randint
from ANNIEMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)

from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import (InlineKeyboardButton, CallbackQuery,
                            InlineKeyboardMarkup, Message)
from ANNIEMUSIC.utils import close_markup
from config import BANNED_USERS, SERVER_PLAYLIST_LIMIT
from ANNIEMUSIC import Carbon, app
from ANNIEMUSIC.utils.decorators.language import language, languageCB
from ANNIEMUSIC.utils.inline.playlist import (botplaylist_markup,
                                              get_playlist_markup,
                                              warning_markup)
from ANNIEMUSIC.utils.pastebin import ANNIEBIN
import time
import yt_dlp
from youtube_search import YoutubeSearch
from youtubesearchpython import VideosSearch
from youtubesearchpython import SearchVideos

from ANNIEMUSIC.utils.stream.stream import stream
from typing import Dict, List, Union

from ANNIEMUSIC.core.mongo import mongodb


playlistdb = mongodb.playlist
playlist = []
# Playlist Databse


async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_playlist_names(chat_id: int) -> List[str]:
    _notes = []
    for note in await _get_playlists(chat_id):
        _notes.append(note)
    return _notes


async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    name = name
    _notes = await _get_playlists(chat_id)
    if name in _notes:
        return _notes[name]
    else:
        return False


async def save_playlist(chat_id: int, name: str, note: dict):
    name = name
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )



async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    name = name
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False




# Command
ADDPLAYLIST_COMMAND = ("addplaylist")
PLAYLIST_COMMAND = ("playlist")
DELETEPLAYLIST_COMMAND = ("delplaylist")


@app.on_message(
    filters.command(PLAYLIST_COMMAND)
    & ~BANNED_USERS
)
@language
async def check_playlist(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    msg = _["playlist_4"]
    count = 0
    for shikhar in _playlist:
        _note = await get_playlist(message.from_user.id, shikhar)
        title = _note["title"]
        title = title.title()
        duration = _note["duration"]
        count += 1
        msg += f"\n\n{count}- {title[:70]}\n"
        msg += _["playlist_5"].format(duration)
    link = await ANNIEBIN(msg)
    lines = msg.count("\n")
    if lines >= 17:
        car = os.linesep.join(msg.split(os.linesep)[:17])
    else:
        car = msg
    carbon = await Carbon.generate(car, randint(100, 10000000000))
    await get.delete()
    await message.reply_photo(
        carbon, caption=_["playlist_15"].format(link)
    )




async def get_keyboard(_, user_id):
    keyboard = InlineKeyboard(row_width=5)
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)
    for x in _playlist:
        _note = await get_playlist(user_id, x)
        title = _note["title"]
        title = title.title()
        keyboard.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f"del_playlist {x}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(
            text=_["PL_B_5"],
            callback_data=f"delete_warning",
        ),
        InlineKeyboardButton(
            text=_["CLOSE_BUTTON"], callback_data=f"close"
        ),
    )
    return keyboard, count


@app.on_message(
    filters.command(DELETEPLAYLIST_COMMAND)
    & ~BANNED_USERS
)
@language
async def del_plist_msg(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    keyboard, count = await get_keyboard(_, message.from_user.id)
    await get.edit_text(
        _["playlist_7"].format(count), reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("play_playlist") & ~BANNED_USERS)
@languageCB
async def play_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await CallbackQuery.answer(
                _["playlist_3"],
                show_alert=True,
            )
        except:
            return
    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    result = []
    try:
        await CallbackQuery.answer()
    except:
        pass
    video = True if mode == "v" else None
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    for vidids in _playlist:
        result.append(vidids)
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = (
            e
            if ex_type == "AssistantErr"
            else _["general_3"].format(ex_type)
        )
        return await mystic.edit_text(err)
    return await mystic.delete()

@app.on_message(filters.command("playplaylist") & ~BANNED_USERS)
@languageCB
async def play_playlist_command(client, message, _):
    mode = message.command[1] if len(message.command) > 1 else None
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    
    if not _playlist:
        try:
            return await message.reply(
                _["playlist_3"],
                quote=True,
            )
        except:
            return
    
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    
    try:
        await message.delete()
    except:
        pass
    
    result = []
    video = True if mode == "v" else None
    
    mystic = await message.reply_text(_["play_1"])
    
    for vidids in _playlist:
        result.append(vidids)
    
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = (
            e
            if ex_type == "AssistantErr"
            else _["general_3"].format(ex_type)
        )
        return await mystic.edit_text(err)
    
    return await mystic.delete()
    


import json

# Combined add_playlist function
@app.on_message(
    filters.command(ADDPLAYLIST_COMMAND)
    & ~BANNED_USERS
)
@language
async def add_playlist(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text("**➻ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴏʀ sᴏɴɢ ʟɪɴᴋ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ..**\n\n**➥ ᴇxᴀᴍᴘʟᴇs:**\n\n▷ `/addplaylist Blue Eyes` (ᴘᴜᴛ ᴀ sᴘᴇᴄɪғɪᴄ sᴏɴɢ ɴᴀᴍᴇ)\n\n▷ /addplaylist [ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ] (ᴛᴏ ᴀᴅᴅ ᴀʟʟ sᴏɴɢs ғʀᴏᴍ ᴀ ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛ ɪɴ ʙᴏᴛ ᴘʟᴀʏʟɪsᴛ.)")

    query = message.command[1]
    
    # Check if the provided input is a YouTube playlist link
    if "youtube.com/playlist" in query:
        adding = await message.reply_text("**🎧 ᴀᴅᴅɪɴɢ sᴏɴɢs ɪɴ ᴘʟᴀʏʟɪsᴛ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..**")
        try:
            from pytube import Playlist
            from pytube import YouTube
            
            playlist = Playlist(query)
            video_urls = playlist.video_urls
            
        except Exception as e:
            # Handle exception
            return await message.reply_text(f"Error: {e}")

        if not video_urls:
            return await message.reply_text("**➻ ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋs.\n\n**➥ ᴛʀʏ ᴏᴛʜᴇʀ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ**")

        user_id = message.from_user.id
        for video_url in video_urls:
            video_id = video_url.split("v=")[-1]
            
            try:
                yt = YouTube(video_url)
                title = yt.title
                duration = yt.length
            except Exception as e:
                return await message.reply_text(f"ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴠɪᴅᴇᴏ ɪɴғᴏ: {e}")

            plist = {
                "videoid": video_id,
                "title": title,
                "duration": duration,
            }
            
            await save_playlist(user_id, video_id, plist)
            keyboardes = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("๏ ᴡᴀɴᴛ ʀᴇᴍᴏᴠᴇ ᴀɴʏ sᴏɴɢs? ๏", callback_data=f"open_playlist {user_id}")
                ]
            ]
        )
        await adding.delete()
        return await message.reply_text(text="**➻ ᴀʟʟ sᴏɴɢs ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғʀᴏᴍ ʏᴏᴜʀ ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ✅**\n\n**➥ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀɴʏ sᴏɴɢ ᴛʜᴇɴ ᴄʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.\n\n**▷ ᴄʜᴇᴄᴋ ʙʏ » /playlist**\n\n▷ **ᴘʟᴀʏ ʙʏ » /play**", reply_markup=keyboardes)
        pass
    if "youtube.com/@" in query:
        addin = await message.reply_text("**🎧 ᴀᴅᴅɪɴɢ sᴏɴɢs ɪɴ ᴘʟᴀʏʟɪsᴛ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..**")
        try:
            from pytube import YouTube

            channel_username = query
            videos = YouTube_videos(f"{query}/videos")
            video_urls = [video['url'] for video in videos]

        except Exception as e:
            # Handle exception
            return await message.reply_text(f"Error: {e}")

        if not video_urls:
            return await message.reply_text("**➻ ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ YouTube channel.\n\n**➥ ᴛʀʏ ᴏᴛʜᴇʀ YouTube channel ʟɪɴᴋ**")

        user_id = message.from_user.id
        for video_url in video_urls:
            videosid = query.split("/")[-1].split("?")[0]

            try:
                yt = YouTube(f"https://youtu.be/{videosid}")
                title = yt.title
                duration = yt.length
            except Exception as e:
                return await message.reply_text(f"ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴠɪᴅᴇᴏ ɪɴғᴏ: {e}")

            plist = {
                "videoid": video_id,
                "title": title,
                "duration": duration,
            }

            await save_playlist(user_id, video_id, plist)
            keyboardes = InlineKeyboardMarkup(
            [            
                [
                    InlineKeyboardButton("๏ ᴡᴀɴᴛ ʀᴇᴍᴏᴠᴇ ᴀɴʏ sᴏɴɢs? ๏", callback_data=f"open_playlist {user_id}")
                ]
            ]
        )
        await addin.delete()
        return await message.reply_text(text="**➻ ᴀʟʟ sᴏɴɢs ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғʀᴏᴍ ʏᴏᴜʀ ʏᴏᴜᴛᴜʙᴇ channel ʟɪɴᴋ✅**\n\n**➥ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀɴʏ sᴏɴɢ ᴛʜᴇɴ ᴄʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.\n\n**▷ ᴄʜᴇᴄᴋ ʙʏ » /playlist**\n\n▷ **ᴘʟᴀʏ ʙʏ » /play**", reply_markup=keyboardes)
        pass
    # Check if the provided input is a YouTube video link
    if "https://youtu.be" in query:
        try:
            add = await message.reply_text("**🎧 ᴀᴅᴅɪɴɢ sᴏɴɢs ɪɴ ᴘʟᴀʏʟɪsᴛ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..**")
            from pytube import Playlist
            from pytube import YouTube
            # Extract video ID from the YouTube lin
            videoid = query.split("/")[-1].split("?")[0]
            user_id = message.from_user.id
            thumbnail = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
            _check = await get_playlist(user_id, videoid)
            if _check:
                try:
                    await add.delete()
                    return await message.reply_photo(thumbnail, caption=_["playlist_8"])
                except KeyError:
                    pass

            _count = await get_playlist_names(user_id)
            count = len(_count)
            if count == SERVER_PLAYLIST_LIMIT:
                try:
                    return await message.reply_text(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT))
                except KeyError:
                    pass

            try:
                yt = YouTube(f"https://youtu.be/{videoid}")
                title = yt.title
                duration = yt.length
                thumbnail = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
                plist = {
                    "videoid": videoid,
                    "title": title,
                    "duration": duration,
                }
                await save_playlist(user_id, videoid, plist)

                # Create inline keyboard with remove button
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("๏ Remove from Playlist ๏", callback_data=f"remove_playlist {videoid}")
                        ]
                    ]
                )
                await add.delete()
                await message.reply_photo(thumbnail, caption="**➻ ᴀᴅᴅᴇᴅ sᴏɴɢ ɪɴ ʏᴏᴜʀ ʙᴏᴛ ᴘʟᴀʏʟɪsᴛ✅**\n\n**➥ ᴄʜᴇᴄᴋ ʙʏ » /playlist**\n\n**➥ ᴅᴇʟᴇᴛᴇ ʙʏ » /delplaylist**\n\n**➥ ᴀɴᴅ ᴘʟᴀʏ ʙʏ » /play (ɢʀᴏᴜᴘs ᴏɴʟʏ)**", reply_markup=keyboard)
            except Exception as e:
                print(f"Error: {e}")
                await message.reply_text(str(e))
        except Exception as e:
            return await message.reply_text(str(e))
            pass
    else:
        from ANNIEMUSIC import YouTube
        # Add a specific song by name
        query = " ".join(message.command[1:])
        print(query)

        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            videoid = results[0]["id"]
            # Add these lines to define views and channel_name
            views = results[0]["views"]
            channel_name = results[0]["channel"]

            user_id = message.from_user.id
            _check = await get_playlist(user_id, videoid)
            if _check:
                try:
                    return await message.reply_photo(thumbnail, caption=_["playlist_8"])
                except KeyError:
                    pass

            _count = await get_playlist_names(user_id)
            count = len(_count)
            if count == SERVER_PLAYLIST_LIMIT:
                try:
                    return await message.reply_text(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT))
                except KeyError:
                    pass

            m = await message.reply("**🔄 ᴀᴅᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **")
            title, duration_min, _, _, _ = await YouTube.details(videoid, True)
            title = (title[:50]).title()
            plist = {
                "videoid": videoid,
                "title": title,
                "duration": duration_min,
            }

            await save_playlist(user_id, videoid, plist)

            # Create inline keyboard with remove button
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("๏ Remove from Playlist ๏", callback_data=f"remove_playlist {videoid}")
                    ]
                ]
            )
            await m.delete()
            await message.reply_photo(thumbnail, caption="**➻ ᴀᴅᴅᴇᴅ sᴏɴɢ ɪɴ ʏᴏᴜʀ ʙᴏᴛ ᴘʟᴀʏʟɪsᴛ✅**\n\n**➥ ᴄʜᴇᴄᴋ ʙʏ » /playlist**\n\n**➥ ᴅᴇʟᴇᴛᴇ ʙʏ » /delplaylist**\n\n**➥ ᴀɴᴅ ᴘʟᴀʏ ʙʏ » /play (ɢʀᴏᴜᴘs ᴏɴʟʏ)**", reply_markup=keyboard)

        except KeyError:
            return await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴅᴀᴛᴀ ғᴏʀᴍᴀᴛ ʀᴇᴄᴇɪᴠᴇᴅ.")
        except Exception as e:
            pass

        
@app.on_callback_query(filters.regex("open_playlist") & ~BANNED_USERS)
@languageCB
async def open_playlist(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    if _playlist:
        get = await CallbackQuery.message.edit_text(_["playlist_2"])
    else:
        return await CallbackQuery.message.edit_text(_["playlist_3"])
    keyboard, count = await get_keyboard(_, CallbackQuery.from_user.id)
    await get.edit_text(_["playlist_7"].format(count), reply_markup=keyboard)


@app.on_callback_query(filters.regex("remove_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    deleted = await delete_playlist(
        CallbackQuery.from_user.id, videoid
    )
    if deleted:
        try:
            await CallbackQuery.answer(
                _["playlist_11"], show_alert=True
            )
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(
                _["playlist_12"], show_alert=True
            )
        except:
            return
    keyboards = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("๏ ʀᴇᴄᴏᴠᴇʀ ʏᴏᴜʀ sᴏɴɢ ๏", callback_data=f"recover_playlist {videoid}")
                ]
            ]
        )
    return await CallbackQuery.edit_message_text(
    text="**➻ ʏᴏᴜʀ sᴏɴɢ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ ʙᴏᴛ ᴘʟᴀʏʟɪsᴛ**\n\n**➥ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴄᴏᴠᴇʀ ʏᴏᴜʀ sᴏɴɢ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ ᴛʜᴇɴ ᴄʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ**",
    reply_markup=keyboards
)


@app.on_callback_query(filters.regex("recover_playlist") & ~BANNED_USERS)
@languageCB
async def add_playlist(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _check = await get_playlist(user_id, videoid)
    if _check:
        try:
            return await CallbackQuery.answer(
                _["playlist_8"], show_alert=True
            )
        except:
            return
    _count = await get_playlist_names(user_id)
    count = len(_count)
    if count == SERVER_PLAYLIST_LIMIT:
        try:
            return await CallbackQuery.answer(
                _["playlist_9"].format(SERVER_PLAYLIST_LIMIT),
                show_alert=True,
            )
        except:
            return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = (title[:50]).title()
    plist = {
        "videoid": vidid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, plist)
    try:
        title = (title[:30]).title()
        keyboardss = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("๏ ʀᴇᴍᴏᴠᴇ ᴀɢᴀɪɴ ๏", callback_data=f"remove_playlist {videoid}")
                ]
            ]
        )
        return await CallbackQuery.edit_message_text(text="**➻ ʀᴇᴄᴏᴠᴇʀᴇᴅ sᴏɴɢ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ**\n\n**➥ Cʜᴇᴄᴋ Pʟᴀʏʟɪsᴛ ʙʏ /playlist**\n\n**➥ ᴅᴇʟᴇᴛᴇ ᴘʟᴀʏʟɪsᴛ ʙʏ » /delplaylist**\n\n**➥ ᴀɴᴅ ᴘʟᴀʏ ᴘʟᴀʏʟɪsᴛ ʙʏ » /play**",
            reply_markup=keyboardss
        )
    except:
        return

@app.on_callback_query(filters.regex("add_playlist") & ~BANNED_USERS)
@languageCB
async def add_playlist(client, CallbackQuery, _):
    await CallbackQuery.answer("➻ ᴛᴏ ᴀᴅᴅ ᴀ sᴏɴɢ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ ᴊᴜsᴛ ᴛʏᴘᴇ /addplaylist (Here your song name)\n\n➥ ᴇxᴀᴍᴘʟᴇ » /addplaylist Blue Eyes Blue tyes.", show_alert=True)
    

@app.on_callback_query(filters.regex("jarvis_playlist") & ~BANNED_USERS)
@languageCB
async def add_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _check = await get_playlist(user_id, videoid)
    if _check:
        try:
            from ANNIEMUSIC import YouTube
            return await CallbackQuery.answer(
                _["playlist_8"], show_alert=True
            )
        except:
            return
    _count = await get_playlist_names(user_id)
    count = len(_count)
    if count == SERVER_PLAYLIST_LIMIT:
        try:
            return await CallbackQuery.answer(
                _["playlist_9"].format(SERVER_PLAYLIST_LIMIT),
                show_alert=True,
            )
        except:
            return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = (title[:50]).title()
    plist = {
        "videoid": vidid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, plist)
    try:
        title = (title[:30]).title()
        return await CallbackQuery.answer(
            _["playlist_10"].format(title), show_alert=True
        )
    except:
        return

# New command
DELETE_ALL_PLAYLIST_COMMAND = ("delallplaylist")

@app.on_message(filters.command(DELETE_ALL_PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def delete_all_playlists(client, message, _):
    from ANNIEMUSIC import YouTube
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        try:
            upl = warning_markup(_)
            await message.reply_text(_["playlist_14"], reply_markup=upl)
        except:
            pass
    else:
        await message.reply_text(_["playlist_3"])

        
@app.on_callback_query(filters.regex("del_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    deleted = await delete_playlist(
        CallbackQuery.from_user.id, videoid
    )
    if deleted:
        try:
            await CallbackQuery.answer(
                _["playlist_11"], show_alert=True
            )
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(
                _["playlist_12"], show_alert=True
            )
        except:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=keyboard
    )



@app.on_callback_query(
    filters.regex("delete_whole_playlist") & ~BANNED_USERS
)
@languageCB
async def del_whole_playlist(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    for x in _playlist:
        await CallbackQuery.answer("➻ ᴏᴋ sɪʀ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.\n\n➥ ᴅᴇʟᴇᴛɪɴɢ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ...", show_alert=True)
        await delete_playlist(CallbackQuery.from_user.id, x)
    return await CallbackQuery.edit_message_text(_["playlist_13"])


@app.on_callback_query(
    filters.regex("get_playlist_playmode") & ~BANNED_USERS
)
@languageCB
async def get_playlist_playmode_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = get_playlist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(
    filters.regex("delete_warning") & ~BANNED_USERS
)
@languageCB
async def delete_warning_message(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    try:
        await CallbackQuery.answer()
    except:
        pass
    upl = warning_markup(_)
    return await CallbackQuery.edit_message_text(
        _["playlist_14"], reply_markup=upl
    )


@app.on_callback_query(filters.regex("home_play") & ~BANNED_USERS)
@languageCB
async def home_play_(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = botplaylist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(
    filters.regex("del_back_playlist") & ~BANNED_USERS
)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    from ANNIEMUSIC import YouTube
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        try:
            await CallbackQuery.answer(
                _["playlist_2"], show_alert=True
            )
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(
                _["playlist_3"], show_alert=True
            )
        except:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_text(
        _["playlist_7"].format(count), reply_markup=keyboard
    )
