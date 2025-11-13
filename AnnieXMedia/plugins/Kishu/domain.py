from pyrogram import filters
from datetime import datetime, timezone
import socket
import requests
import whois

from AnnieXMedia import app

def get_domain_info(domain_name):
    try:
        return whois.whois(domain_name)
    except Exception as e:
        print(f"[WHOIS Error] {e}")
        return None

def get_domain_age(creation_date):
    if isinstance(creation_date, list):
        creation_date = creation_date[0]
    return (datetime.now(timezone.utc) - creation_date).days // 365 if creation_date else None

def get_ip_location(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.ok:
            data = response.json()
            return data if data.get("status") == "success" else None
    except Exception as e:
        print(f"[IP Geo Error] {e}")
    return None

def format_info(info):
    def clean(item):
        if isinstance(item, list):
            return item[0] if item else None
        return item

    domain = clean(info.domain_name)
    registrar = clean(info.registrar)
    creation = clean(info.creation_date)
    expiry = clean(info.expiration_date)
    nameservers = ', '.join(info.name_servers) if info.name_servers else "N/A"
    age = get_domain_age(creation)

    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = "Unavailable"

    location_data = get_ip_location(ip)
    location = f"{location_data['country']}, {location_data['city']}" if location_data else "Unavailable"

    return (
        f"**ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ**: {domain}\n"
        f"**ʀᴇɢɪsᴛʀᴀʀ**: {registrar}\n"
        f"**ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ**: {creation.strftime('%Y-%m-%d') if creation else 'N/A'}\n"
        f"**ᴇxᴘɪʀᴀᴛɪᴏɴ ᴅᴀᴛᴇ**: {expiry.strftime('%Y-%m-%d') if expiry else 'N/A'}\n"
        f"**ᴅᴏᴍᴀɪɴ ᴀɢᴇ**: {age} years\n"
        f"**ɪᴘ ᴀᴅᴅʀᴇss**: `{ip}`\n"
        f"**ʟᴏᴄᴀᴛɪᴏɴ**: {location}\n"
        f"**ɴᴀᴍᴇsᴇʀᴠᴇʀs**: {nameservers}\n"
    )

@app.on_message(filters.command("domain"))
async def domain_lookup(_, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a domain name. Example: `/domain heroku.com`")

    domain_name = message.text.split(maxsplit=1)[1].strip()
    data = get_domain_info(domain_name)

    if not data:
        return await message.reply("⚠️ Failed to retrieve WHOIS data.")

    response = format_info(data)
    await message.reply(response)
