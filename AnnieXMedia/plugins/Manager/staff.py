import asyncio
import html

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired
from pyrogram.types import Message

from AnnieXMedia import app

def _in_group(msg: Message) -> bool:
    return msg.chat and msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)

def _mention_html(user) -> str:
    name = html.escape((user.first_name or "User").strip())
    return f'<a href="tg://user?id={user.id}">{name}</a>'

@app.on_message(filters.command(["admins", "staff"]))
async def list_admins(_: Message):
    message = _
    if not _in_group(message):
        return await message.reply_text(
            "<i>Use this in a group or supergroup.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        owners, admins = [], []
        async for m in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            if (getattr(m, "privileges", None) and getattr(m.privileges, "is_anonymous", False)) or m.user.is_bot:
                continue
            if m.status == ChatMemberStatus.OWNER:
                owners.append(m.user)
            else:
                admins.append(m.user)

        title = html.escape(message.chat.title or "this chat")
        txt = f"<b>Group Staff – {title}</b>\n\n"
        owner_line = _mention_html(owners[0]) if owners else "<i>Hidden</i>"
        txt += f"<b>Owner</b>\n└ {owner_line}\n\n<b>Admins</b>\n"

        if not admins:
            txt += "└ <i>No visible admins</i>"
        else:
            for i, adm in enumerate(admins):
                branch = "└" if i == len(admins) - 1 else "├"
                handle = f"@{adm.username}" if adm.username else _mention_html(adm)
                txt += f"{branch} {handle}\n"

        txt += f"\n<b>Total Admins</b>: {len(owners) + len(admins)}"
        await app.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "<i>I need admin rights to list admins here.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

@app.on_message(filters.command("bots"))
async def list_bots(_: Message):
    message = _
    if not _in_group(message):
        return await message.reply_text(
            "<i>Use this in a group or supergroup.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        bots = []
        async for b in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            bots.append(b.user)

        title = html.escape(message.chat.title or "this chat")
        txt = f"<b>Bot List – {title}</b>\n\n<b>Bots</b>\n"
        if not bots:
            txt += "└ <i>No bots</i>"
        else:
            for i, bt in enumerate(bots):
                branch = "└" if i == len(bots) - 1 else "├"
                handle = f"@{bt.username}" if bt.username else _mention_html(bt)
                txt += f"{branch} {handle}\n"
        txt += f"\n<b>Total Bots</b>: {len(bots)}"
        await app.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "<i>I need admin rights to list bots here.</i>",
            parse_mode=enums.ParseMode.HTML,
        )