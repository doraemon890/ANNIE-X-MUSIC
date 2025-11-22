# Authored By Certified Coders © 2025
import aiohttp
import html
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode

from AnnieXMedia import app


def _safe(x: str | None) -> str:
    return html.escape(x or "")

def _short(t: str, n: int = 350) -> str:
    t = t.strip()
    return (t[: n - 1] + "…") if len(t) > n else t

def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "N/A"
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return iso


@app.on_message(filters.command(["github", "git"]))
async def github(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "<b>ᴜsᴀɢᴇ:</b> <code>/git &lt;username&gt;</code>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    username = message.command[1].strip()
    api = f"https://api.github.com/users/{username}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 404:
                    return await message.reply_text(
                        "🚫 <b>ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!</b>",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                if r.status == 403:
                    return await message.reply_text(
                        "⚠️ <b>ʀᴀᴛᴇ ʟɪᴍɪᴛ ʜɪᴛ. ᴛʀʏ ᴀɢᴀɪɴ sᴏᴏɴ.</b>",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                if r.status != 200:
                    return await message.reply_text(
                        f"⚠️ <b>ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ (HTTP {r.status}).</b>",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                data = await r.json()
        except Exception as e:
            return await message.reply_text(
                f"⚠️ <b>ʀᴇQᴜᴇsᴛ ꜰᴀɪʟᴇᴅ:</b> <code>{html.escape(str(e))}</code>",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    name = _safe(data.get("name") or "Not specified")
    bio = _short(_safe(data.get("bio") or "No bio available."))
    blog_raw = (data.get("blog") or "").strip()
    blog_is_url = blog_raw.lower().startswith(("http://", "https://"))
    blog_disp = _safe(blog_raw) if blog_raw else "N/A"
    location = _safe(data.get("location") or "Unknown")
    company = _safe(data.get("company") or "N/A")
    created = _safe(_fmt_date(data.get("created_at")))
    profile_url = data.get("html_url") or ""
    repos = _safe(str(data.get("public_repos", "0")))
    followers = _safe(str(data.get("followers", "0")))
    following = _safe(str(data.get("following", "0")))
    avatar = data.get("avatar_url") or None

    if blog_is_url:
        blog_disp = f'<a href="{html.escape(blog_raw)}">{blog_disp}</a>'

    profile_link = (
        f'<a href="{html.escape(profile_url)}">ᴠɪᴇᴡ ᴏɴ ɢɪᴛʜᴜʙ</a>' if profile_url else "N/A"
    )

    caption = (
        "<b>✨ ɢɪᴛʜᴜʙ ᴘʀᴏғɪʟᴇ ɪɴꜰᴏ</b>\n\n"
        f"👤 <b>ɴᴀᴍᴇ:</b> <code>{name}</code>\n"
        f"🔧 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> <code>{_safe(username)}</code>\n"
        f"📌 <b>ʙɪᴏ:</b> {bio}\n"
        f"🏢 <b>ᴄᴏᴍᴘᴀɴʏ:</b> {company}\n"
        f"📍 <b>ʟᴏᴄᴀᴛɪᴏɴ:</b> {location}\n"
        f"🌐 <b>ʙʟᴏɢ:</b> {blog_disp}\n"
        f"🗓 <b>ᴄʀᴇᴀᴛᴇᴅ ᴏɴ:</b> <code>{created}</code>\n"
        f"📁 <b>ᴘᴜʙʟɪᴄ ʀᴇᴘᴏs:</b> <code>{repos}</code>\n"
        f"👥 <b>ғᴏʟʟᴏᴡᴇʀs:</b> <code>{followers}</code> | "
        f"<b>ғᴏʟʟᴏᴡɪɴɢ:</b> <code>{following}</code>\n"
        f"🔗 <b>ᴘʀᴏғɪʟᴇ:</b> {profile_link}"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]]
    )

    if avatar:
        await message.reply_photo(
            photo=avatar,
            caption=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
