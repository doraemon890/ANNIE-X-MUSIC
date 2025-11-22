# Authored By Certified Coders © 2025
from pyrogram import Client, filters
from pyrogram.types import Message
import httpx
from AnnieXMedia import app


def chunk_string(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


@app.on_message(filters.command("allrepo"))
async def all_repo_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please enter a GitHub username.\n\nExample: `/allrepo CertifiedCoders`")

    username = message.command[1].strip()

    try:
        repo_info = await get_all_repository_info(username)

        if not repo_info:
            return await message.reply_text("❌ No public repositories found or user does not exist.")

        chunks = chunk_string(repo_info, 4000)

        for chunk in chunks:
            await message.reply_text(chunk, disable_web_page_preview=True)

    except Exception as e:
        print(f"Error in /allrepo: {e}")
        await message.reply_text("⚠️ An error occurred while fetching repositories.")


async def get_all_repository_info(username: str) -> str:
    url = f"https://api.github.com/users/{username}/repos"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    if not data:
        return None

    info_lines = [
        f"🖇 **[{repo['name']}]({repo['html_url']})**\n"
        f"⭐ Stars: `{repo['stargazers_count']}` | 🍴 Forks: `{repo['forks_count']}`\n"
        f"📄 {repo['description'] or 'No description'}"
        for repo in data
    ]

    profile_link = f"👤 [View GitHub Profile](https://github.com/{username})"
    return f"{profile_link}\n\n" + "\n\n".join(info_lines)
