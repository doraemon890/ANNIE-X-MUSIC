import os
from PIL import Image, ImageDraw, ImageFont
from pyrogram import enums, filters
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import TopicClosed, PeerIdInvalid, ChannelPrivate, SlowmodeWait
from ANNIEMUSIC import app
from ANNIEMUSIC.mongo.welcomedb import is_on, set_state, bump, cool, auto_on

BG_PATH = "ANNIEMUSIC/assets/annie/welcome.png"
FALLBACK_PIC = "ANNIEMUSIC/assets/upic.png"
FONT_PATH = "ANNIEMUSIC/assets/annie/Arimo.ttf"
BTN_VIEW = "๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏"
BTN_ADD = "๏ ᴋɪᴅɴᴀᴘ ᴍᴇ ๏"

CAPTION_TXT = """
**❅────✦ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ✦────❅
{chat_title}
▰▰▰▰▰▰▰▰▰▰▰▰▰
➻ Nᴀᴍᴇ ✧ {mention}
➻ Iᴅ ✧ `{uid}`
➻ Usᴇʀɴᴀᴍᴇ ✧ @{uname}
➻ Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs ✧ {count}
▰▰▰▰▰▰▰▰▰▰▰▰▰**
**❅─────✧❅✦❅✧─────❅**
"""

JOIN_THRESHOLD = 20
TIME_WINDOW = 10
COOL_MINUTES = 5
WELCOME_LIMIT = 5

last_messages: dict[int, list] = {}


def _cooldown_minutes(burst: int, threshold: int = JOIN_THRESHOLD, base: int = COOL_MINUTES) -> int:
    if burst < threshold:
        return 0
    extra = max(0, burst - threshold)
    return min(60, base + extra * 2)


def _circle(im, size=(835, 839)):
    im = im.resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *size), fill=255)
    im.putalpha(mask)
    return im


def build_pic(av, fn, uid, un):
    bg = Image.open(BG_PATH).convert("RGBA")
    avatar = _circle(Image.open(av))
    bg.paste(avatar, (1887, 390), avatar)
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(FONT_PATH, 65)
    draw.text((421, 715), fn, fill=(242, 242, 242), font=font)
    draw.text((270, 1005), str(uid), fill=(242, 242, 242), font=font)
    draw.text((570, 1308), un, fill=(242, 242, 242), font=font)
    path = f"downloads/welcome_{uid}.png"
    bg.save(path)
    return path


@app.on_message(filters.command("welcome") & filters.group)
async def toggle(client, m: Message):
    usage = "**Usage:**\n⦿/welcome [on|off]\n➤ Annie Special Welcome....."
    if len(m.command) != 2:
        return await m.reply_text(usage)
    u = await client.get_chat_member(m.chat.id, m.from_user.id)
    if u.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await m.reply_text("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ sᴛᴀᴛᴜs!**")
    flag = m.command[1].lower()
    if flag not in ("on", "off"):
        return await m.reply_text(usage)
    cur = await is_on(m.chat.id)
    if flag == "off" and not cur:
        return await m.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
    if flag == "on" and cur:
        return await m.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
    await set_state(m.chat.id, flag)
    await m.reply_text(f"**{'ᴇɴᴀʙʟᴇᴅ' if flag == 'on' else 'ᴅɪsᴀʙʟᴇᴅ'} ᴡᴇʟᴄᴏᴍᴇ ɪɴ {m.chat.title}**")


@app.on_chat_member_updated(filters.group, group=-3)
async def welcome(client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    cid = update.chat.id
    if not (new and new.status == enums.ChatMemberStatus.MEMBER):
        return
    valid_old_statuses = (enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED)
    if old and (old.status not in valid_old_statuses):
        return

    # ✅ Ensure bot is in the chat before sending messages
    try:
        me = await client.get_me()
        try:
            await client.get_chat_member(cid, me.id)
        except (ChannelPrivate, PeerIdInvalid, Exception):
            return
    except Exception:
        pass

    if not await is_on(cid):
        if await auto_on(cid):
            try:
                await client.send_message(cid, "**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ʀᴇ-ᴇɴᴀʙʟᴇᴅ.**")
            except TopicClosed:
                return
            except (ChannelPrivate, PeerIdInvalid, SlowmodeWait):
                return
            except Exception:
                return
        else:
            return

    burst = await bump(cid, TIME_WINDOW)
    if burst >= JOIN_THRESHOLD:
        minutes = _cooldown_minutes(burst, JOIN_THRESHOLD, COOL_MINUTES)
        await cool(cid, minutes)
        try:
            return await client.send_message(
                cid,
                f"**ᴍᴀssɪᴠᴇ ᴊᴏɪɴ ᴅᴇᴛᴇᴄᴛᴇᴅ (x{burst}). ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ғᴏʀ {minutes} ᴍɪɴᴜᴛᴇs.**"
            )
        except TopicClosed:
            return
        except (ChannelPrivate, PeerIdInvalid, SlowmodeWait):
            return
        except Exception:
            return

    user = new.user
    avatar = img = None
    try:
        try:
            if user.photo and getattr(user.photo, 'big_file_id', None):
                avatar = await client.download_media(user.photo.big_file_id, file_name=f"downloads/pp_{user.id}.png")
            else:
                avatar = FALLBACK_PIC
        except (PeerIdInvalid, ChannelPrivate, SlowmodeWait):
            return
        except Exception:
            avatar = FALLBACK_PIC

        img = build_pic(avatar, user.first_name, user.id, user.username or "No Username")

        try:
            members = await client.get_chat_members_count(cid)
        except (ChannelPrivate, PeerIdInvalid, SlowmodeWait):
            return
        except Exception:
            members = "?"

        caption = CAPTION_TXT.format(
            chat_title=update.chat.title,
            mention=user.mention,
            uid=user.id,
            uname=user.username or "No Username",
            count=members
        )

        try:
            sent = await client.send_photo(
                cid,
                img,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(BTN_VIEW, url=f"tg://openmessage?user_id={user.id}")],
                    [InlineKeyboardButton(BTN_ADD, url=f"https://t.me/{client.username}?startgroup=true")],
                ])
            )
        except TopicClosed:
            return
        except (PeerIdInvalid, ChannelPrivate, SlowmodeWait):
            return

        last_messages.setdefault(cid, []).append(sent)
        if len(last_messages[cid]) > WELCOME_LIMIT:
            old_msg = last_messages[cid].pop(0)
            try:
                await old_msg.delete()
            except:
                pass

    except TopicClosed:
        return
    except (PeerIdInvalid, ChannelPrivate, SlowmodeWait):
        return
    except Exception:
        # fallback: try to send a simple text welcome if everything else failed
        try:
            await client.send_message(cid, f"🎉 Welcome, {user.mention}!")
        except (TopicClosed, ChannelPrivate, PeerIdInvalid, SlowmodeWait):
            return
        except Exception:
            return
    finally:
        for f in (avatar, img):
            if f and os.path.exists(f) and "ANNIEMUSIC/assets" not in f:
                try:
                    os.remove(f)
                except:
                    pass
