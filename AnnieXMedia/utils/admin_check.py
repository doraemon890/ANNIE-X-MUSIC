from pyrogram.types import CallbackQuery
from pyrogram.enums import ChatType, ChatMemberStatus

async def is_admin(message_or_cq) -> bool:
    if isinstance(message_or_cq, CallbackQuery):
        message = message_or_cq.message
    else:
        message = message_or_cq

    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP]:
        return False

    if message.from_user.id in [777000, 1087968824]:
        return True

    client = message._client
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

async def is_group_owner(message_or_cq) -> bool:
    if isinstance(message_or_cq, CallbackQuery):
        message = message_or_cq.message
    else:
        message = message_or_cq

    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP]:
        return False

    if message.from_user.id in [777000, 1087968824]:
        return True

    client = message._client
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status == ChatMemberStatus.OWNER
