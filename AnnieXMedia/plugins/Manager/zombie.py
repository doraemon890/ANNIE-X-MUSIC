import asyncio
import html
from typing import List

from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired, RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from AnnieXMedia import app
from AnnieXMedia.utils.admin_check import is_admin

chatQueue: set[int] = set()
stopProcess: bool = False


def _in_group(msg: Message) -> bool:
    return msg.chat and msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)


def _mention_html(user) -> str:
    name = html.escape((user.first_name or "User").strip())
    return f'<a href="tg://user?id={user.id}">{name}</a>'


async def _bot_is_admin(chat_id: int) -> bool:
    try:
        me = await app.get_chat_member(chat_id, "self")
        return me.status == ChatMemberStatus.ADMINISTRATOR
    except RPCError:
        return False


async def scan_deleted_members(chat_id: int) -> List:
    users = []
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user and member.user.is_deleted:
                users.append(member.user)
    except (ChannelInvalid, ChatAdminRequired):
        return []
    return users


async def safe_edit(msg: Message, text: str):
    try:
        await msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass
    except Exception:
        pass


@app.on_message(filters.command(["zombies"]))
async def prompt_zombie_cleanup(_: Client, message: Message):
    if not _in_group(message):
        return await message.reply_text(
            "👥 <b>Use this in a group or supergroup.</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    if not await is_admin(message):
        return await message.reply_text(
            "👮🏻 | <b>Only admins can execute this command.</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    if not await _bot_is_admin(message.chat.id):
        return await message.reply_text(
            "➠ | <b>I need admin rights to scan & remove deleted accounts.</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    deleted_list = await scan_deleted_members(message.chat.id)
    if not deleted_list:
        return await message.reply_text(
            "⟳ | <b>No deleted accounts found in this chat.</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    total = len(deleted_list)
    est_time = max(1, total // 5)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes, Clean", callback_data=f"confirm_zombies:{message.chat.id}"
                ),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_zombies"),
            ]
        ]
    )

    await message.reply_text(
        (
            f"⚠️ | <b>Found <code>{total}</code> deleted accounts.</b>\n"
            f"⏳ | <b>Estimated cleanup time:</b> <code>{est_time}s</code>\n\n"
            "Do you want to clean them?"
        ),
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_callback_query(filters.regex(r"^confirm_zombies"))
async def execute_zombie_cleanup(_: Client, cq: CallbackQuery):
    global stopProcess

    try:
        chat_id = int(cq.data.split(":", 1)[1])
    except Exception:
        return await cq.answer("Invalid request.", show_alert=True)

    if not await is_admin(cq):
        return await cq.answer("👮🏻 | Only admins can confirm this action.", show_alert=True)

    if not await _bot_is_admin(chat_id):
        try:
            return await cq.edit_message_text(
                "➠ | <b>I need admin rights to remove deleted accounts.</b>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            return

    if chat_id in chatQueue:
        return await cq.answer("⚠️ | Cleanup already in progress.", show_alert=True)

    chatQueue.add(chat_id)

    deleted_list = await scan_deleted_members(chat_id)
    total = len(deleted_list)

    try:
        status = await cq.edit_message_text(
            f"🧭 | <b>Found <code>{total}</code> deleted accounts.</b>\n🥀 | <b>Starting cleanup...</b>",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception:
        status = cq.message

    removed = 0

    async def ban_member(user_id: int) -> bool:
        try:
            await app.ban_chat_member(chat_id, user_id)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await ban_member(user_id)
        except (ChannelInvalid, ChatAdminRequired):
            return False
        except Exception:
            return False

    tasks = []
    for user in deleted_list:
        if stopProcess:
            break
        tasks.append(ban_member(user.id))

    batch_size = 20
    for i in range(0, len(tasks), batch_size):
        results = await asyncio.gather(*tasks[i : i + batch_size], return_exceptions=True)
        removed += sum(1 for r in results if r is True)
        await safe_edit(
            status,
            f"♻️ | <b>Removed {removed}/{total} deleted accounts...</b>",
        )
        await asyncio.sleep(2)

    chatQueue.discard(chat_id)
    await safe_edit(
        status, f"✅ | <b>Successfully removed <code>{removed}</code> out of <code>{total}</code> zombies.</b>"
    )


@app.on_callback_query(filters.regex(r"^cancel_zombies$"))
async def cancel_zombie_cleanup(_: Client, cq: CallbackQuery):
    try:
        await cq.edit_message_text("❌ | <b>Cleanup cancelled.</b>", parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass


@app.on_message(filters.command(["admins", "staff"]))
async def list_admins(_: Client, message: Message):
    if not _in_group(message):
        return await message.reply_text(
            "👥 <b>Use this in a group or supergroup.</b>",
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
        txt += f"👑 <b>Owner</b>\n└ {owner_line}\n\n👮🏻 <b>Admins</b>\n"

        if not admins:
            txt += "└ <i>No visible admins</i>"
        else:
            for i, adm in enumerate(admins):
                branch = "└" if i == len(admins) - 1 else "├"
                handle = f"@{adm.username}" if adm.username else _mention_html(adm)
                txt += f"{branch} {handle}\n"

        txt += f"\n✅ | <b>Total Admins</b>: {len(owners) + len(admins)}"
        await app.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "➠ | <b>I need admin rights to list admins here.</b>",
            parse_mode=enums.ParseMode.HTML,
        )


@app.on_message(filters.command("bots"))
async def list_bots(_: Client, message: Message):
    if not _in_group(message):
        return await message.reply_text(
            "👥 <b>Use this in a group or supergroup.</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        bots = [
            b.user
            async for b in app.get_chat_members(
                message.chat.id, filter=enums.ChatMembersFilter.BOTS
            )
        ]
        title = html.escape(message.chat.title or "this chat")
        txt = f"<b>Bot List – {title}</b>\n\n🤖 <b>Bots</b>\n"
        for i, bt in enumerate(bots):
            branch = "└" if i == len(bots) - 1 else "├"
            handle = f"@{bt.username}" if bt.username else _mention_html(bt)
            txt += f"{branch} {handle}\n"
        txt += f"\n✅ | <b>Total Bots</b>: {len(bots)}"
        await app.send_message(message.chat.id, txt, parse_mode=enums.ParseMode.HTML)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except (ChannelInvalid, ChatAdminRequired):
        await message.reply_text(
            "➠ | <b>I need admin rights to list bots here.</b>",
            parse_mode=enums.ParseMode.HTML,
        )