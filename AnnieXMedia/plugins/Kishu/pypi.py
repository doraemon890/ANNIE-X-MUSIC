# Authored By Certified Coders © 2025
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import requests
from AnnieXMedia import app


def get_pypi_info(package_name):
    try:
        api_url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching PyPI information: {e}")
        return None


@app.on_message(filters.command("pypi"))
async def pypi_info_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**❌ Please provide a Python package name.**\n\nExample: `/pypi requests`",
            parse_mode=ParseMode.MARKDOWN
        )

    package_name = message.command[1]
    pypi_info = get_pypi_info(package_name)

    if pypi_info:
        info = pypi_info['info']
        project_url = info['project_urls'].get('Homepage') or info.get('home_page', 'N/A')

        info_message = (
            f"📦 **Package Name:** `{info['name']}`\n"
            f"🆕 **Latest Version:** `{info['version']}`\n"
            f"📝 **Description:** {info['summary'] or 'No description provided.'}\n"
            f"🔗 **Project URL:** [Click here]({project_url})"
        )

        await message.reply_text(info_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply_text(
            "**❌ Please provide a valid Python package name.**\n"
            "It might be misspelled or not published on PyPI.",
            parse_mode=ParseMode.MARKDOWN
        )
