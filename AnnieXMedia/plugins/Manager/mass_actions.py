"""
-------------------------------------------------------------------------
Mass/group administration commands with owner‑only confirmation:

• /kickall   – kick all non‑admin members  
• /banall    – ban all non‑admin members  
• /unbanall  – unban all previously banned members  
• /muteall   – mute all non‑admin members  
• /unmuteall – unmute all non‑admin members  
• /unpinall  – unpin all messages  

Only the group owner or sudoers can run these.  
Each command asks for a Yes/No confirmation via inline buttons.
-------------------------------------------------------------------------
"""

import asyncio

from pyrogram import filters, Client
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    CallbackQuery, Message, ChatPermissions
)
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter

from AnnieXMedia import app
from AnnieXMedia.utils.permissions import is_owner_or_sudoer, mention

MASS_CMDS = ["kickall", "banall", "unbanall", "muteall", "unmuteall", "unpinall"]


def _confirmation_keyboard(cmd: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data=f"{cmd}_yes"),
         InlineKeyboardButton("No",  callback_data=f"{cmd}_no")]
    ])


@app.on_message(filters.command(MASS_CMDS) & filters.group)
async def ask_mass_confirm(client: Client, message: Message):
    cmd = message.command[0]
    ok, owner = await is_owner_or_sudoer(client, message.chat.id, message.from_user.id)
    if not ok:
        owner_m = mention(owner.id, owner.first_name) if owner else "the owner"
        return await message.reply_text(
            f"❌ Only {owner_m} may run “{cmd}”."
        )

    await message.reply_text(
        f"⚠️ {message.from_user.mention}, confirm `{cmd}` for this group?",
        reply_markup=_confirmation_keyboard(cmd)
    )


@app.on_callback_query(filters.regex(rf"^({'|'.join(MASS_CMDS)})_(yes|no)$"))
async def handle_mass_confirm(client: Client, callback: CallbackQuery):
    data = callback.data
    cmd, answer = data.split("_")
    chat_id = callback.message.chat.id
    uid = callback.from_user.id

    ok, owner = await is_owner_or_sudoer(client, chat_id, uid)
    if not ok:
        return await callback.answer("Only the group owner can confirm.", show_alert=True)

    if answer == "no":
        return await callback.message.edit(f"❌ `{cmd}` canceled.")

    bot_member = await client.get_chat_member(chat_id, client.me.id)
    priv = bot_member.privileges
    needed = {
        "kickall":   priv.can_restrict_members,
        "banall":    priv.can_restrict_members,
        "unbanall":  priv.can_restrict_members,
        "muteall":   priv.can_restrict_members,
        "unmuteall": priv.can_restrict_members,
        "unpinall":  priv.can_pin_messages,
    }
    if not needed.get(cmd, False):
        return await callback.message.edit("❌ I lack necessary permissions.")

    await callback.message.edit(f"⏳ `{cmd}` in progress…")

    try:
        if cmd == "kickall":
            await _do_kickall(client, chat_id)
        elif cmd == "banall":
            await _do_banall(client, chat_id)
        elif cmd == "unbanall":
            await _do_unbanall(client, chat_id)
        elif cmd == "muteall":
            await _do_muteall(client, chat_id)
        elif cmd == "unmuteall":
            await _do_unmuteall(client, chat_id)
        elif cmd == "unpinall":
            await _do_unpinall(client, chat_id)

        await callback.message.edit(f"✅ `{cmd}` completed.")
    except Exception as e:
        await callback.message.edit(f"❌ Error during `{cmd}`:\n{e}")


# ─────────────────────────────────────────────────────
# Implementations
# ─────────────────────────────────────────────────────
async def _do_kickall(client, chat_id: int):
    kicked, errors = 0, 0
    async for m in client.get_chat_members(chat_id):
        if m.user.is_bot or m.status == ChatMemberStatus.OWNER:
            continue
        try:
            await client.ban_chat_member(chat_id, m.user.id)
            await asyncio.sleep(0.1)
            await client.unban_chat_member(chat_id, m.user.id)
            kicked += 1
        except:
            errors += 1
        await asyncio.sleep(0.05)
    await client.send_message(chat_id, f"Kicked: {kicked}\nFailures: {errors}")


async def _do_banall(client, chat_id: int):
    banned, errors = 0, 0
    async for m in client.get_chat_members(chat_id):
        if m.user.is_bot or m.status == ChatMemberStatus.OWNER:
            continue
        try:
            await client.ban_chat_member(chat_id, m.user.id)
            banned += 1
        except:
            errors += 1
        await asyncio.sleep(0.05)
    await client.send_message(chat_id, f"Banned: {banned}\nFailures: {errors}")



async def _do_unbanall(client, chat_id: int):
    unbanned, errors = 0, 0
    async for m in client.get_chat_members(chat_id, filter=ChatMembersFilter.BANNED):
        try:
            await client.unban_chat_member(chat_id, m.user.id)
            unbanned += 1
        except:
            errors += 1
        await asyncio.sleep(0.05)
    await client.send_message(chat_id, f"Unbanned: {unbanned}\nFailures: {errors}")


async def _do_muteall(client, chat_id: int):
    muted, errors = 0, 0
    perms = ChatPermissions()
    async for m in client.get_chat_members(chat_id):
        if m.user.is_bot or m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            continue
        try:
            await client.restrict_chat_member(chat_id, m.user.id, perms)
            muted += 1
        except:
            errors += 1
        await asyncio.sleep(0.05)
    await client.send_message(chat_id, f"Muted: {muted}\nFailures: {errors}")


async def _do_unmuteall(client, chat_id: int):
    unmuted, errors = 0, 0
    perms = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    )
    async for m in client.get_chat_members(chat_id):
        if m.user.is_bot or m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            continue
        try:
            await client.restrict_chat_member(chat_id, m.user.id, perms)
            unmuted += 1
        except:
            errors += 1
        await asyncio.sleep(0.05)
    await client.send_message(chat_id, f"Unmuted: {unmuted}\nFailures: {errors}")


async def _do_unpinall(client, chat_id: int):
    try:
        await client.unpin_all_chat_messages(chat_id)
        await client.send_message(chat_id, "Unpinned all messages.")
    except Exception as e:
        await client.send_message(chat_id, f"Failed to unpin messages:\n{e}")
