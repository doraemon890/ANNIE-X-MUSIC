from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

IPINFO_TOKEN = '434e1cea389a93'
IPQUALITYSCORE_API_KEY = 'Y0OZMypz71dEF9HxxQd21J2xvqUE0BVS'

@app.on_message(filters.command(["ip"]))
def ip_info_and_score(_, message):
    if len(message.command) != 2:
        message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀɴ **ɪᴘ** ᴀᴅᴅʀᴇss ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ. ᴇxᴀᴍᴘʟᴇ**:** /ip 8.8.8.8")
        return

    ip_address = message.command[1]
    ip_info = get_ip_info(ip_address)
    ip_score = get_ip_score(ip_address, IPQUALITYSCORE_API_KEY)

    if ip_info is not None and ip_score is not None:
        response_message = (
            f"{ip_info}\n"
            f"**ɪᴘ sᴄᴏʀᴇ**➪ {ip_score}"
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
                f"**ɪᴘ**➪ {data.get('ip', 'N/A')}\n"
                f"**ᴄɪᴛʏ**➪ {data.get('city', 'N/A')}\n"
                f"**ʀᴇɢɪᴏɴ**➪ {data.get('region', 'N/A')}\n"
                f"**ᴄᴏᴜɴᴛʀʏ**➪ {data.get('country', 'N/A')}\n"
                f"**ʟᴏᴀᴛɪᴏɴ**➪ {data.get('loc', 'N/A')}\n"
                f"**ᴏʀɢᴀɴɪsᴀᴛɪᴏɴ**➪ {data.get('org', 'N/A')}\n"
                f"**ᴘᴏsᴛᴀʟ ᴄᴏᴅᴇ**➪ {data.get('postal', 'N/A')}\n"
                f"**ᴛɪᴍᴇᴢᴏɴᴇ**➪ {data.get('timezone', 'N/A')}"
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
            return data.get('fraud_score', 'N/A')
    except Exception as e:
        print(f"Error fetching IP score: {e}")
    return None
