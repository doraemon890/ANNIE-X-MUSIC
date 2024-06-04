from pyrogram import Client, filters
import requests
from ANNIEMUSIC import app

@app.on_message(filters.command(["ip"]))
def ip_info(_, message):
    if len(message.command) != 2:
        message.reply_text("Please provide an IP address after the command. Example: /ip 8.8.8.8")
        return

    ip_address = message.command[1]
    info = get_ip_info(ip_address)

    if info:
        message.reply_text(info)
    else:
        message.reply_text("Unable to fetch information for the provided IP address.")

def get_ip_info(ip_address):
    api_url = f"https://ipinfo.io/{ip_address}?token=434e1cea389a93"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            info = (
                f"**IP**: {data.get('ip', 'N/A')}\n"
                f"**City**: {data.get('city', 'N/A')}\n"
                f"**Region**: {data.get('region', 'N/A')}\n"
                f"**Country**: {data.get('country', 'N/A')}\n"
                f"**Location**: {data.get('loc', 'N/A')}\n"
                f"**Organization**: {data.get('org', 'N/A')}\n"
                f"**Postal Code**: {data.get('postal', 'N/A')}\n"
                f"**Timezone**: {data.get('timezone', 'N/A')}"
            )
            return info
    except Exception as e:
        print(f"Error fetching IP information: {e}")
    return None
