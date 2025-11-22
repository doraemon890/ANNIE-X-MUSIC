# Authored By Certified Coders © 2025
from AnnieXMedia.core.mongo import mongodb

impdb = mongodb["pretender"]

async def usr_data(user_id: int) -> bool:
    return bool(await impdb.find_one({"user_id": user_id}))

async def get_userdata(user_id: int):
    user = await impdb.find_one({"user_id": user_id})
    if not user:
        return None, None, None
    return user.get("username"), user.get("first_name"), user.get("last_name")

async def add_userdata(user_id: int, username, first_name, last_name):
    await impdb.update_one(
        {"user_id": user_id},
        {"$set": {"username": username, "first_name": first_name, "last_name": last_name}},
        upsert=True,
    )

async def check_pretender(chat_id: int) -> bool:
    return bool(await impdb.find_one({"chat_id_toggle": chat_id}))

async def impo_on(chat_id: int):
    await impdb.update_one({"chat_id_toggle": chat_id}, {"$set": {"chat_id_toggle": chat_id}}, upsert=True)

async def impo_off(chat_id: int):
    await impdb.delete_one({"chat_id_toggle": chat_id})
