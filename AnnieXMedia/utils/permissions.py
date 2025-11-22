# Authored By Certified Coders © 2025
import datetime as dt
from typing import Tuple, Optional

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram.types import Message, User
from pyrogram.errors import RPCError

from AnnieXMedia.misc import SUDOERS
from AnnieXMedia.logging import LOGGER


# ────────────────────────────────────────────────────────────
# tiny util
# ────────────────────────────────────────────────────────────
def mention(user_id: int, name: str) -> str:
    return f"[{name}](tg://user?id={user_id})"


# ────────────────────────────────────────────────────────────
# string‑time parsing (10s / 5m / 2h / 3d)
# ────────────────────────────────────────────────────────────
def parse_time(time_str: str) -> Optional[dt.timedelta]:
    if len(time_str) < 2:
        return None
    unit = time_str[-1].lower()
    if unit not in {"s", "m", "h", "d"}:
        return None
    try:
        value = int(time_str[:-1])
    except ValueError:
        return None
    if unit == "s":
        return dt.timedelta(seconds=value)
    if unit == "m":
        return dt.timedelta(minutes=value)
    if unit == "h":
        return dt.timedelta(hours=value)
    if unit == "d":
        return dt.timedelta(days=value)
    return None


# ────────────────────────────────────────────────────────────
# User / reason / title extractors (reply, @user, or ID)
# ────────────────────────────────────────────────────────────
async def _resolve_user(client: Client, identifier: str | int) -> Optional[User]:
    try:
        return await client.get_users(identifier)
    except RPCError:
        return None


async def extract_user_and_reason(
    message: Message, client: Client
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Accepts:
      • reply
      • `/cmd @user | id [reason ...]`
    Returns (user_id, first_name, reason)
    """
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    else:
        if len(message.command) < 2:
            await message.reply_text("Specify a user or reply to someone.")
            return None, None, None
        target_user = await _resolve_user(client, message.command[1])
        if not target_user:
            await message.reply_text("I can’t find that user.")
            return None, None, None
        reason = message.text.partition(message.command[1])[2].strip() or None

    return target_user.id, target_user.first_name, reason


async def extract_user_and_title(
    message: Message, client: Client
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    For /promote variants → returns (user_id, first_name, title)
    """
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        title = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    else:
        if len(message.command) < 2:
            await message.reply_text("Specify a user or reply to someone.")
            return None, None, None
        target_user = await _resolve_user(client, message.command[1])
        if not target_user:
            await message.reply_text("I can’t find that user.")
            return None, None, None
        title = message.text.partition(message.command[1])[2].strip() or None

    return target_user.id, target_user.first_name, title


# ────────────────────────────────────────────────────────────
# Group owner / sudo helpers (used by mass_actions.py)
# ────────────────────────────────────────────────────────────
async def get_group_owner(client: Client, chat_id: int):
    async for member in client.get_chat_members(
        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        if member.status == ChatMemberStatus.OWNER:
            return member.user
    return None


async def is_owner_or_sudoer(client: Client, chat_id: int, user_id: int):
    owner_user = await get_group_owner(client, chat_id)
    if owner_user and (user_id == owner_user.id or user_id in SUDOERS):
        return True, owner_user
    return False, owner_user


# ────────────────────────────────────────────────────────────
# Generic permission check (bot or user)
# ────────────────────────────────────────────────────────────
async def user_has_permission(
    client: Client,
    chat_title: str,
    chat_id: int,
    user_id: int,
    permission: str,
    *,
    is_bot: bool = True,
) -> Tuple[bool, Optional[str]]:
    """
    Check a specific privilege on a user (or bot). Returns (has_perm, error_txt)
    """
    if user_id in SUDOERS:
        return True, None

    try:
        member = await client.get_chat_member(chat_id, user_id)
        flags = member.privileges
        has_perm = getattr(flags, permission, False)
    except Exception as exc:  # noqa: BLE001
        LOGGER(__name__).warning("perm‑check failed: %s", exc)
        has_perm = False

    if not has_perm:
        who = "I" if is_bot else "You"
        txt = f"{who} don’t have the right **{permission}** in **{chat_title}**."
        return False, txt
    return True, None
