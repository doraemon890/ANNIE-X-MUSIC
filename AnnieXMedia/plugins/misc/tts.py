import asyncio
import os
from math import ceil
from typing import Dict, List, Tuple

import edge_tts
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from AnnieXMedia import app

# ---------------------------------------------------------------------------
# Global caches & constants
# ---------------------------------------------------------------------------
_voice_sessions: Dict[Tuple[int, int], str] = {}
_voices: List[dict] = []
_languages: List[str] = []
_VOICES_LOCK = asyncio.Lock()

PER_ROW = 4          # 4 buttons per row
PER_PAGE = 16        # 4 × 4 grid per page
TMP_DIR = "/tmp"   # location for temporary audio / text files

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
async def _init_voices() -> None:
    """Populate the global voice cache exactly once (with coroutine safety)."""
    global _voices, _languages
    if _voices:  # already cached
        return

    async with _VOICES_LOCK:
        if _voices:  # may have been populated while waiting for the lock
            return

        raw = await edge_tts.list_voices()
        _voices = [
            {
                "short_name": v["ShortName"],
                "locale": v["Locale"],
                "gender": v["Gender"],
            }
            for v in raw
        ]
        _languages = sorted({v["locale"].split("-", 1)[0] for v in _voices})


def _paginate(items: List[str], page: int) -> Tuple[List[str], int]:
    """Return the slice for *page* (1-based) and the total number of pages."""
    total = len(items)
    pages = max(1, ceil(total / PER_PAGE))
    page = max(1, min(page, pages))
    start = (page - 1) * PER_PAGE
    return items[start : start + PER_PAGE], pages


def _build_keyboard(
    items: List[str],
    step: str,
    extra: Dict[str, str],
    page: int,
) -> InlineKeyboardMarkup:
    """Build an inline keyboard for the current *step* with navigation."""
    page_items, total_pages = _paginate(items, page)

    # item buttons
    rows: List[List[InlineKeyboardButton]] = []
    for i in range(0, len(page_items), PER_ROW):
        chunk = page_items[i : i + PER_ROW]
        rows.append(
            [
                InlineKeyboardButton(
                    text=item,
                    callback_data="tts:"
                    + f"s={step}"
                    + "".join(f"|{k}={v}" for k, v in extra.items())
                    + f"|p={page}|v={item}",
                )
                for item in chunk
            ]
        )

    # navigation row
    nav: List[InlineKeyboardButton] = []
    if page > 1:
        nav.append(
            InlineKeyboardButton(
                "◀️ Prev",
                callback_data="tts:"
                + f"s={step}"
                + "".join(f"|{k}={v}" for k, v in extra.items())
                + f"|p={page-1}",
            )
        )
    if page < total_pages:
        nav.append(
            InlineKeyboardButton(
                "Next ▶️",
                callback_data="tts:"
                + f"s={step}"
                + "".join(f"|{k}={v}" for k, v in extra.items())
                + f"|p={page+1}",
            )
        )
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(rows)


def _session_key(chat_id: int, user_id: int) -> Tuple[int, int]:
    return chat_id, user_id


def _cleanup(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


async def _synthesize(voice: str, text: str, out_path: str) -> None:
    """Generate an MP3 file using edge-TTS."""
    comm = edge_tts.Communicate(text=text, voice=voice)
    await comm.save(out_path)

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
@app.on_message(filters.command("voices"))
async def cmd_voices(client: Client, message: Message):
    """Start interactive TTS selection."""
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide the text to convert.\n\nExample: `/voices Hello world`",
            parse_mode=ParseMode.MARKDOWN,
        )

    await _init_voices()

    text = message.text.split(" ", 1)[1]
    _voice_sessions[_session_key(message.chat.id, message.from_user.id)] = text

    kb = _build_keyboard(_languages, step="lang", extra={}, page=1)
    await message.reply_text(
        "🌐 **Step 1:** Select a language",
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN,
    )


@app.on_message(filters.command("tts"))
async def cmd_tts(client: Client, message: Message):
    """Direct `/tts <voice> <text>` command."""
    if len(message.command) < 3:
        return await message.reply_text(
            "❌ Usage:\n`/tts <voice_model> <text>`\nAlternatively try `/voices` for guided selection.",
            parse_mode=ParseMode.MARKDOWN,
        )

    await _init_voices()

    voice = message.command[1]
    text = message.text.split(" ", 2)[2]

    if not any(v["short_name"] == voice for v in _voices):
        return await message.reply_text(
            f"⚠️ Unknown voice: `{voice}`\nUse `/voiceall` or `/voices` to browse voices.",
            parse_mode=ParseMode.MARKDOWN,
        )

    tmp = os.path.join(TMP_DIR, f"tts_{message.from_user.id}.mp3")
    try:
        await client.send_chat_action(message.chat.id, ChatAction.RECORD_AUDIO)
        await _synthesize(voice, text, tmp)

        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_AUDIO)
        await client.send_audio(
            chat_id=message.chat.id,
            audio=tmp,
            caption=f"🗣️ `{voice}`",
            reply_to_message_id=message.id,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[TTS DIRECT ERROR] {exc}")
        await message.reply_text("⚠️ Failed to generate speech.")
    finally:
        _cleanup(tmp)


@app.on_callback_query(filters.regex(r"^tts:"))
async def cb_tts(client: Client, callback: CallbackQuery):
    """Inline-keyboard callback handler for the /voices workflow."""
    data = callback.data[4:]
    parts = dict(p.split("=", 1) for p in data.split("|") if "=" in p)
    step = parts.get("s")
    page = int(parts.get("p", "1"))

    await _init_voices()

    key = _session_key(callback.message.chat.id, callback.from_user.id)
    text = _voice_sessions.get(key)
    if not text:
        return await callback.answer(
            "⚠️ Session expired. Send `/voices` again.", show_alert=True
        )

    # -------------------- language level --------------------
    if step == "lang":
        if "v" not in parts:  # show languages
            kb = _build_keyboard(_languages, "lang", {}, page)
            return await callback.message.edit_text(
                "🌐 **Step 1:** Select a language",
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )

        lang = parts["v"]  # language chosen → regions
        regions = sorted(
            {
                v["locale"].split("-", 1)[1]
                for v in _voices
                if v["locale"].startswith(f"{lang}-")
            }
        )
        kb = _build_keyboard(regions, "region", {"l": lang}, 1)
        return await callback.message.edit_text(
            "🌍 **Step 2:** Select a region",
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )

    # -------------------- region level --------------------
    if step == "region":
        lang = parts["l"]

        if "v" not in parts:  # show regions
            regions = sorted(
                {
                    v["locale"].split("-", 1)[1]
                    for v in _voices
                    if v["locale"].startswith(f"{lang}-")
                }
            )
            kb = _build_keyboard(regions, "region", {"l": lang}, page)
            return await callback.message.edit_text(
                "🌍 **Step 2:** Select a region",
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )

        # region chosen → show models
        region = parts["v"]
        locale = f"{lang}-{region}"
        models = sorted([v["short_name"] for v in _voices if v["locale"] == locale])
        kb = _build_keyboard(models, "model", {"l": lang, "r": region}, 1)
        return await callback.message.edit_text(
            "🔊 **Step 3:** Choose a voice model",
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )

    # -------------------- model level --------------------
    if step == "model":
        lang = parts["l"]
        region = parts["r"]

        if "v" not in parts:  # show models
            locale = f"{lang}-{region}"
            models = sorted([v["short_name"] for v in _voices if v["locale"] == locale])
            kb = _build_keyboard(models, "model", {"l": lang, "r": region}, page)
            return await callback.message.edit_text(
                "🔊 **Step 3:** Choose a voice model",
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )

        # model chosen → synthesize
        voice = parts["v"]
        tmp = os.path.join(TMP_DIR, f"tts_{callback.from_user.id}.mp3")
        try:
            await client.send_chat_action(callback.message.chat.id, ChatAction.RECORD_AUDIO)
            await _synthesize(voice, text, tmp)

            await client.send_chat_action(callback.message.chat.id, ChatAction.UPLOAD_AUDIO)
            await client.send_audio(
                chat_id=callback.message.chat.id,
                audio=tmp,
                caption=f"🗣️ `{voice}`",
                reply_to_message_id=callback.message.id,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[TTS CALLBACK ERROR] {exc}")
            await callback.message.reply_text(f"⚠️ Generation failed:\n`{exc}`")
        finally:
            _cleanup(tmp)
            _voice_sessions.pop(key, None)
        return await callback.answer()

    # ------------------------------------------------------------------
    # Unknown action
    await callback.answer("🤔 Unknown action. Send /voices again.", show_alert=True)


@app.on_message(filters.command("voiceall"))
async def cmd_voiceall(client: Client, message: Message):
    """Send a text file listing all voices."""
    await _init_voices()

    lines = [
        f"{v['short_name']} — {v['locale']} ({v['gender']})" for v in _voices
    ]
    path = os.path.join(TMP_DIR, f"voices_{message.from_user.id}.txt")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))

    await message.reply_document(document=path, caption="📋 List of all available voices")
    _cleanup(path)
