from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

IPINFO_TOKEN = 'de9e66ca96b47e'
IPQUALITYSCORE_API_KEY = '952ztTq41AxoXam43pStVjVNcEjo1ntQ'

@app.on_message(filters.command(["ip"]))
def ip_info_and_score(_, message):
    if len(message.command) != 2:
        message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀɴ **ɪᴘ** ᴀᴅᴅʀᴇss ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ. ᴇxᴀᴍᴘʟᴇ**:** /ip 8.8.8.8")
        return

    ip_address = message.command[1]
    ip_info = get_ip_info(ip_address)
    ip_score, score_description, emoji = get_ip_score(ip_address, IPQUALITYSCORE_API_KEY)

    if ip_info is not None and ip_score is not None:
        response_message = (
            f"{ip_info}\n\n"
            f"**ɪᴘ sᴄᴏʀᴇ** ➪ {ip_score} {emoji} ({score_description})"
        )
        message.reply_text(response_message)
    else:
        message.reply_text("Unable to fetch information for the provided IP address.")

def get_ip_info(ip_address):
    api_url = f"https://ipinfo.io/{ip_address}?token={IPINFO_TOKEN}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            info = (
                f"🌐 **ɪᴘ** ➪ {data.get('ip', 'N/A')}\n"
                f"🏙️ **ᴄɪᴛʏ** ➪ {data.get('city', 'N/A')}\n"
                f"📍 **ʀᴇɢɪᴏɴ** ➪ {data.get('region', 'N/A')}\n"
                f"🌍 **ᴄᴏᴜɴᴛʀʏ** ➪ {data.get('country', 'N/A')}\n"
                f"📌 **ʟᴏᴄᴀᴛɪᴏɴ** ➪ {data.get('loc', 'N/A')}\n"
                f"🏢 **ᴏʀɢᴀɴɪᴢᴀᴛɪᴏɴ** ➪ {data.get('org', 'N/A')}\n"
                f"📮 **ᴘᴏsᴛᴀʟ ᴄᴏᴅᴇ** ➪ {data.get('postal', 'N/A')}\n"
                f"⏰ **ᴛɪᴍᴇᴢᴏɴᴇ** ➪ {data.get('timezone', 'N/A')}"
            )
            return info
    except Exception as e:
        print(f"Error fetching IP information: {e}")
    return None

def get_ip_score(ip_address, api_key):
    api_url = f"https://ipqualityscore.com/api/json/ip/{api_key}/{ip_address}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            fraud_score = data.get('fraud_score', 'N/A')
            if fraud_score != 'N/A':
                fraud_score = int(fraud_score)
                if fraud_score <= 20:
                    score_description = 'Good'
                    emoji = '✅'
                elif fraud_score <= 60:
                    score_description = 'Moderate'
                    emoji = '⚠️'
                else:
                    score_description = 'Bad'
                    emoji = '❌'
                return fraud_score, score_description, emoji
    except Exception as e:
        print(f"Error fetching IP score: {e}")
    return None, None, None
