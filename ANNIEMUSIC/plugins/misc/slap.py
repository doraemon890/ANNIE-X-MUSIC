from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

@app.on_message(filters.command("slap") & ~filters.forwarded & ~filters.via_bot)
def slap_command(client, message):
    try:

        sender = message.from_user.mention(style='markdown')

        target = sender if not message.reply_to_message else message.reply_to_message.from_user.mention(style='markdown')

        
        response = requests.get("https://api.waifu.pics/sfw/slap")
        response.raise_for_status()

        gif_url = response.json().get("url")

        if gif_url:
            msg = f"{sender} slapped {target}! 😒"
            message.reply_animation(animation=gif_url, caption=msg)
        else:
            message.reply_text("Couldn't retrieve the animation. Please try again.")
        
    except requests.exceptions.RequestException as e:
        message.reply_text(f"An error occurred while making the request: {e}")
    except Exception as e:
        
        message.reply_text(f"An unexpected error occurred: {str(e)}")
