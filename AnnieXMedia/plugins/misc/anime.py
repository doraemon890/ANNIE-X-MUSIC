from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from AnnieXMedia import app
import httpx
import re


async def get_anime_info(anime_name):
    url = 'https://graphql.anilist.co'
    query = '''
    query ($anime: String) {
      Media (search: $anime, type: ANIME) {
        id
        title {
          romaji
          english
          native
        }
        description(asHtml: false)
        episodes
        status
        averageScore
        coverImage {
          large
        }
      }
    }
    '''
    variables = {"anime": anime_name}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json={'query': query, 'variables': variables})

    data = response.json()

    if 'errors' in data:
        return None, f"❌ Error: {data['errors'][0]['message']}"

    return data['data']['Media'], None


def clean_description(desc):
    if not desc:
        return "No description available."
    desc = re.sub(r"<br\s*/?>", "\n", desc)
    desc = re.sub(r"<[^>]+>", "", desc)
    return desc.strip()[:800] + "..." if len(desc) > 800 else desc


@app.on_message(filters.command("anime"))
async def anime_info(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide an anime name.\n\nExample: `/anime Naruto`",
            parse_mode=ParseMode.MARKDOWN
        )

    anime_name = " ".join(message.command[1:])
    result, error = await get_anime_info(anime_name)

    if not result:
        return await message.reply_text(
            error or "❌ Anime not found.",
        )

    title = result['title']['romaji']
    english = result['title'].get('english')
    native = result['title']['native']
    episodes = result.get('episodes', 'N/A')
    status = result.get('status', 'N/A')
    score = result.get('averageScore', 'N/A')
    desc = clean_description(result.get('description'))
    image = result['coverImage']['large']

    english_line = f"**🇺🇸 Title (English):** {english}\n" if english else ""

    caption = (
        f"**🎌 Title (Romaji):** {title}\n"
        f"{english_line}"
        f"**🈶 Title (Native):** {native}\n"
        f"**📺 Episodes:** {episodes}\n"
        f"**📊 Score:** {score}/100\n"
        f"**📌 Status:** {status}\n\n"
        f"**📝 Description:**\n{desc}"
    )

    await message.reply_photo(
        image,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
    )
