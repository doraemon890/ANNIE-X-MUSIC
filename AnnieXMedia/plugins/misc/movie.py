# Authored By Certified Coders © 2025
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from AnnieXMedia import app
import httpx


TMDB_API_KEY = "23c3b139c6d59ebb608fe6d5b974d888"
TMDB_BASE = "https://api.themoviedb.org/3"


@app.on_message(filters.command("movie"))
async def movie_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide a movie name.\n\nExample: `/movie Inception`",
            parse_mode=ParseMode.MARKDOWN
        )

    movie_name = " ".join(message.command[1:])
    status = await message.reply_text("🔎 Searching for the movie...")

    try:
        info = await get_movie_info(movie_name)
        await status.edit_text(info, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"[Movie Error] {e}")
        await status.edit_text("❌ Failed to fetch movie information.")


async def get_movie_info(query: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        search = await client.get(f"{TMDB_BASE}/search/movie", params={
            "api_key": TMDB_API_KEY,
            "query": query
        })
        search_data = search.json()
        if not search_data.get("results"):
            return "❌ Movie not found."

        movie = search_data["results"][0]
        movie_id = movie["id"]

        details = await client.get(f"{TMDB_BASE}/movie/{movie_id}", params={
            "api_key": TMDB_API_KEY
        })
        details_data = details.json()

        cast = await client.get(f"{TMDB_BASE}/movie/{movie_id}/credits", params={
            "api_key": TMDB_API_KEY
        })
        cast_data = cast.json()
        actors = ", ".join([actor["name"] for actor in cast_data.get("cast", [])[:5]]) or "N/A"

        title = details_data.get("title", "N/A")
        release = details_data.get("release_date", "N/A")
        overview = details_data.get("overview", "N/A")
        rating = details_data.get("vote_average", "N/A")
        revenue = details_data.get("revenue", 0)

        revenue_str = f"${revenue:,}" if revenue else "Not Available"

        info = (
            f"🎬 **Title:** {title}\n"
            f"📅 **Release Date:** {release}\n"
            f"⭐ **Rating:** {rating}/10\n"
            f"🎭 **Top Cast:** {actors}\n"
            f"💰 **Box Office:** {revenue_str}\n\n"
            f"📝 **Overview:**\n{overview}"
        )

        return info
