# Authored By Certified Coders © 2025
import asyncio
import html

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import ChannelInvalid, ChatAdminRequired, FloodWait
from pyrogram.types import Message

from AnnieXMedia import app


def _in_group(msg: Message) -> bool:
    return bool(msg.chat and msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP))


def _mention_html(user) -> str:
    name = html.escape((user.first_name or "User").strip())
    return f'<a href="tg://user?id={user.id}">{name}</a>'


@app.on_message(filters.command(["admins", "staff"]))
async def list_admins(client, message: Message):
    if not _in_group(message):
        return await message.reply_text(
            "⚠️ <i>Use this in a group or supergroup.</i>",
            parse_mode=enums.ParseMode.HTML,
        )
    try:
        owners = []
        human_admins = []
        bot_admins = []

        async for member in client.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            if getattr(member, "privileges", None) and getattr(
                member.privileges, "is_anonymous", False
            ):
                continue

            user = member.user
            if member.status == ChatMemberStatus.OWNER:
                owners.append(user)
            else:
                if user.is_bot:
                    bot_admins.append(user)
                else:
                    human_admins.append(user)

        title = html.escape(message.chat.title or "this chat")
        txt = f"🛡 <b>Group Staff — {title}</b>\n\n"

        owner_line = (
            _mention_html(owners[0])
            if owners
            else "<i>Hidden Owner</i>"
        )

        txt += f"<b>Owner</b>\n└ {owner_line}\n\n"

        txt += "<b>👤 Admins</b>\n"
        if not human_admins:
            txt += "└ <i>No human admins</i>\n"
        else:
            for i, adm in enumerate(human_admins):
                branch = "└" if i == len(human_admins) - 1 else "├"
                handle = (
                    f"@{adm.username}"
                    if adm.username
                    else _mention_html(adm)
                )
                txt += f"{branch} {handle}\n"

        txt += "\n<b>🤖 Bot Admins</b>\n"
        if not bot_admins:
            txt += "└ <i>No bot admins</i>\n"
        else:
            for i, adm in enumerate(bot_admins):
                branch = "└" if i == len(bot_admins) - 1 else "├"
                handle = (
                    f"@{adm.username}"
                    if adm.username
                    else _mention_html(adm)
                )
                txt += f"{branch} {handle}\n"

        total = len(owners) + len(human_admins) + len(bot_admins)
        txt += f"\n<b>Total Admins:</b> {total}"

        await client.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "❌ <i>I need admin rights to list admins here.</i>",
            parse_mode=enums.ParseMode.HTML,
        )


@app.on_message(filters.command("bots"))
async def list_bots(client, message: Message):
    if not _in_group(message):
        return await message.reply_text(
            "⚠️ <i>Use this in a group or supergroup.</i>",
            parse_mode=enums.ParseMode.HTML,
        )
    try:
        bots = []

        async for b in client.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            is_admin = b.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            )
            bots.append((b.user, is_admin))

        title = html.escape(message.chat.title or "this chat")
        txt = f"🤖 <b>Bot List — {title}</b>\n\n<b>Bots</b>\n"

        if not bots:
            txt += "└ <i>No bots found</i>\n"
        else:
            for i, (bt, is_admin) in enumerate(bots):
                branch = "└" if i == len(bots) - 1 else "├"
                handle = (
                    f"@{bt.username}"
                    if bt.username
                    else _mention_html(bt)
                )
                admin_flag = " <b>— Admin</b> 🛡" if is_admin else ""
                txt += f"{branch} {handle}{admin_flag}\n"

        txt += f"\n<b>Total Bots:</b> {len(bots)}"

        await client.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "❌ <i>I need admin rights to list bots here.</i>",
            parse_mode=enums.ParseMode.HTML,
        )
