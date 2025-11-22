# Authored By Certified Coders © 2025
# Authored By Certified Coders © 2025

import os
import json
import shutil
import zipfile
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import Message
from AnnieXMedia import app
from config import MONGO_DB_URI, LOGGER_ID, OWNER_ID
from AnnieXMedia.logging import LOGGER
from AnnieXMedia.core.dir import BACKUP_DIR

DB_NAME = "Annie"
TEMP_DIR = os.path.join(BACKUP_DIR, "tmp")

async def _dump_collection(collection, path: str):
    data = []
    async for doc in collection.find({}):
        doc.pop("_id", None)
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        data.append(doc)
    if data:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

async def _create_backup_zip() -> str:
    LOGGER(__name__).info("🗂️ Starting backup process for all collections…")

    client = AsyncIOMotorClient(MONGO_DB_URI)
    db = client[DB_NAME]
    collections = await db.list_collection_names()

    for fname in os.listdir(BACKUP_DIR):
        fpath = os.path.join(BACKUP_DIR, fname)
        if os.path.isfile(fpath) and fname.endswith(".zip"):
            try:
                os.remove(fpath)
            except Exception:
                pass

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    tasks = [
        _dump_collection(db[coll], os.path.join(TEMP_DIR, f"{coll}.json"))
        for coll in collections
    ]
    await asyncio.gather(*tasks)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"AnnieXMedia_Backup_{timestamp}.zip"
    zip_path = os.path.join(BACKUP_DIR, zip_name)

    LOGGER(__name__).info(f"📦 Creating backup archive: {zip_name}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(TEMP_DIR):
            for file in files:
                fp = os.path.join(root, file)
                arc = os.path.join("Annie", os.path.relpath(fp, TEMP_DIR))
                zf.write(fp, arc)

    shutil.rmtree(TEMP_DIR)
    return zip_path

async def _send_backup(zip_path: str, chat_id: int, caption: str):
    await app.send_document(chat_id=chat_id, document=zip_path, caption=caption)
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except Exception:
            pass

@app.on_message(filters.command("backup") & filters.user(OWNER_ID))
async def manual_backup(_: Client, message: Message):
    processing = await message.reply_text(
        "🔐 **Starting Backup…**\n"
        "__Please wait while we securely export your database.__ 🚀"
    )
    try:
        zip_path = await _create_backup_zip()
        caption = (
            "✅ **Backup Successfully Completed!**\n"
            "__Your MongoDB database has been exported.__ 📁✨\n\n"
            f"**File:** `{os.path.basename(zip_path)}`"
        )
        await _send_backup(zip_path, message.chat.id, caption)
        await processing.delete()
    except Exception as e:
        await processing.edit_text(
            "❌ **Backup Failed!**\n"
            f"**Error:** `{e}`"
        )
        LOGGER(__name__).error(f"Manual backup failed: {e}")

async def daily_backup_task():
    while True:
        now = datetime.now()
        target = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        try:
            zip_path = await _create_backup_zip()
            caption = (
                "🕛 **Daily Backup — Completed☑️**\n"
                "__Your automatic full database backup is ready.__ 🔒📦"
            )
            await _send_backup(zip_path, LOGGER_ID, caption)
            LOGGER(__name__).info("Daily backup sent to LOGGER_ID.")
        except Exception as e:
            LOGGER(__name__).error(f"Daily backup failed: {e}")

asyncio.create_task(daily_backup_task())
