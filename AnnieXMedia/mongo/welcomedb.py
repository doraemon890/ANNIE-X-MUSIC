from datetime import datetime, timedelta, timezone
from typing import Optional
from AnnieXMedia.core.mongo import mongodb

_col = mongodb["welcome"]


async def is_on(chat_id: int) -> bool:
    doc = await _col.find_one({"_id": chat_id}, {"state": 1})
    return (doc or {}).get("state", "on") == "on"


async def set_state(chat_id: int, flag: str) -> None:
    if flag not in ("on", "off"):
        raise ValueError("flag must be 'on' or 'off'")
    await _col.update_one({"_id": chat_id}, {"$set": {"state": flag}}, upsert=True)


async def bump(chat_id: int, time_window: int = 8) -> int:
    now = datetime.now(timezone.utc)
    doc = await _col.find_one({"_id": chat_id}, {"last_ts": 1, "join_cnt": 1})
    last_ts: Optional[datetime] = doc.get("last_ts") if doc else None

    if last_ts and last_ts.tzinfo is None:
        last_ts = last_ts.replace(tzinfo=timezone.utc)

    if last_ts and (now - last_ts).total_seconds() <= time_window:
        cnt = int((doc.get("join_cnt") or 0)) + 1
    else:
        cnt = 1

    await _col.update_one(
        {"_id": chat_id},
        {"$set": {"last_ts": now, "join_cnt": cnt}},
        upsert=True,
    )
    return cnt


async def cool(chat_id: int, cool_minutes: int = 10) -> None:
    now = datetime.now(timezone.utc)
    await _col.update_one(
        {"_id": chat_id},
        {
            "$set": {
                "state": "off",
                "cool_until": now + timedelta(minutes=cool_minutes),
            }
        },
        upsert=True,
    )


async def auto_on(chat_id: int) -> bool:
    now = datetime.now(timezone.utc)
    doc = await _col.find_one({"_id": chat_id}, {"cool_until": 1})
    cool_until: Optional[datetime] = (doc or {}).get("cool_until")

    if cool_until and cool_until.tzinfo is None:
        cool_until = cool_until.replace(tzinfo=timezone.utc)

    if cool_until and now >= cool_until:
        await _col.update_one(
            {"_id": chat_id},
            {"$set": {"state": "on"}, "$unset": {"cool_until": ""}},
            upsert=True,
        )
        return True
    return False