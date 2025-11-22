# Authored By Certified Coders © 2025
import time
from datetime import datetime
from asyncio import sleep

from pyrogram import filters, enums
from pyrogram.types import Message

from AnnieXMedia import app


@app.on_message(~filters.private & filters.command(["groupdata"]), group=2)
async def groupdata_handler(client, message: Message):
    start_time = time.perf_counter()

    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
            warn = await message.reply_text("🚫 ONLY ADMINS CAN USE THIS!")
            await sleep(5)
            return await warn.delete()
    except Exception:
        warn = await message.reply_text("🚫 Admin check failed.")
        await sleep(5)
        return await warn.delete()

    status = await message.reply_text("🔍 Gathering group stats...")

    try:
        total_members = await client.get_chat_members_count(message.chat.id)
    except Exception:
        total_members = 0

    stats = {
        "banned": 0,
        "deleted": 0,
        "bots": 0,
        "premium": 0,
        "restricted": 0,
        "fake": 0,
        "admins": 0,
        "uncached": 0,
    }

    try:
        async for _ in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BANNED):
            stats["banned"] += 1
    except Exception:
        pass

    try:
        async for _ in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            stats["admins"] += 1
    except Exception:
        pass

    try:
        async for member in client.get_chat_members(message.chat.id):
            u = member.user

            if u.is_deleted:
                stats["deleted"] += 1
                continue

            if u.is_bot:
                stats["bots"] += 1
                continue

            if getattr(u, "is_premium", False):
                stats["premium"] += 1

            if getattr(member, "status", None) == enums.ChatMemberStatus.RESTRICTED:
                stats["restricted"] += 1

            if (u.username is None) and (u.first_name is not None) and (len(u.first_name) <= 2):
                stats["fake"] += 1
            else:
                stats["uncached"] += 1
    except Exception:
        pass

    end_time = time.perf_counter()
    took = f"{end_time - start_time:.2f}"
    now = datetime.now().strftime("%d %b %Y • %H:%M")
    title = message.chat.title or "This Group"

    text = (
        f"<b>📊 Group Data Report</b>\n"
        f"<i>{now}</i>\n"
        f"────────────────────────\n"
        f"<b>🧩 Group</b>: {title}\n"
        f"<b>👥 Members</b>: <code>{total_members:,}</code>\n"
        f"────────────────────────\n"
        f"<b>👮 Admins</b>: <code>{stats['admins']:,}</code>\n"
        f"<b>🤖 Bots</b>: <code>{stats['bots']:,}</code>\n"
        f"<b>🧟 Zombies</b>: <code>{stats['deleted']:,}</code>\n"
        f"<b>🚫 Banned</b>: <code>{stats['banned']:,}</code>\n"
        f"<b>🎁 Premium</b>: <code>{stats['premium']:,}</code>\n"
        f"<b>🔒 Restricted</b>: <code>{stats['restricted']:,}</code>\n"
        f"<b>👻 Fake</b>: <code>{stats['fake']:,}</code>\n"
        f"────────────────────────\n"
        f"<b>⏱ Time taken</b>: <code>{took}s</code>"
    )

    await status.edit(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )
