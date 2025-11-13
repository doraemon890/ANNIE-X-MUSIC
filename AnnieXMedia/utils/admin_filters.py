from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from AnnieXMedia.utils.admin_check import is_admin, is_group_owner
from AnnieXMedia.misc import SUDOERS
from config import OWNER_ID


def sudo_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    return bool(
        (
            (msg.from_user and msg.from_user.id in SUDOERS)
            or (msg.sender_chat and msg.sender_chat.id in SUDOERS)
        )
        and not getattr(msg, "edit_date", False)
    )

sudo_filter = filters.create(func=sudo_filter_func, name="SudoUsersFilter")


async def admin_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    if getattr(msg, "edit_date", False):
        return False
    return await is_admin(msg)

admin_filter = filters.create(func=admin_filter_func, name="AdminFilter")


async def group_owner_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    if getattr(msg, "edit_date", False):
        return False
    return await is_group_owner(msg)

owner_filter = filters.create(func=group_owner_filter_func, name="GroupOwnerFilter")


def bot_owner_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    return (
        msg.from_user
        and msg.from_user.id == OWNER_ID
        and not getattr(msg, "edit_date", False)
    )

dev_filter = filters.create(func=bot_owner_filter_func, name="BotOwnerFilter")
