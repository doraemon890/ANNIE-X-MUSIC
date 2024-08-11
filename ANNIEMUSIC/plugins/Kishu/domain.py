from pyrogram import Client, filters
import whois
import socket
from datetime import datetime
import requests
from ANNIEMUSIC import app

def get_domain_hosting_info(domain_name):
    try:
        return whois.whois(domain_name)
    except whois.parser.PywhoisError as e:
        print(f"Error: {e}")
        return None

def calculate_domain_age(creation_date):
    if isinstance(creation_date, list):
        creation_date = creation_date[0]
    return (datetime.now() - creation_date).days // 365 if creation_date else None

def get_ip_geolocation(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            return data if data.get("status") == "success" else None
    except Exception as e:
        print(f"Error retrieving geolocation: {e}")
    return None

def format_domain_info(domain_info):
    def format_list(item):
        return ', '.join(item) if isinstance(item, list) else item

    age = calculate_domain_age(domain_info.creation_date)
    ip = socket.gethostbyname(format_list(domain_info.domain_name))
    geo_info = get_ip_geolocation(ip)

    response = (
        f"**ᴅᴏᴍᴀɪɴ ɴᴀᴍᴇ**: {format_list(domain_info.domain_name)}\n"
        f"**ʀᴇɢɪsᴛʀᴀʀ**: {domain_info.registrar}\n"
        f"**ʀᴇɢɪsᴛʀᴀʀ ᴜʀʟ**: {domain_info.registrar_url}\n"
        f"**ᴄʀᴇᴀᴛɪᴏɴ ᴅᴀᴛᴇ**: {domain_info.creation_date}\n"
        f"**ᴇxᴘɪʀᴀᴛɪᴏɴ ᴅᴀᴛᴇ**: {domain_info.expiration_date}\n"
        f"**ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇᴅ**: {domain_info.updated_date}\n"
        f"**ᴅᴏᴍᴀɪɴ ᴀɢᴇ**: {age} years\n"
        f"**sᴛᴀᴛᴜs**: {format_list(domain_info.status)}\n"
        f"**ɴᴀᴍᴇsᴇʀᴠᴇʀs**: {format_list(domain_info.name_servers)}\n"
        f"**ɪᴘ ᴀᴅᴅʀᴇss**: `{ip}`\n"
        f"**ʟᴏᴄᴀᴛɪᴏɴ**: {geo_info['country']}, {geo_info['city']}\n" if geo_info else ""
        f"**ᴅɴssᴇᴄ**: {domain_info.dnssec}\n"
        f"**ʀᴇɢɪsᴛʀᴀɴᴛ ɴᴀᴍᴇ**: {domain_info.name}\n"
        f"**ʀᴇɢɪsᴛʀᴀɴᴛ ᴏʀɢᴀɴɪᴢᴀᴛɪᴏɴ**: {domain_info.org}\n"
        f"**ʀᴇɢɪsᴛʀᴀɴᴛ ᴄᴏᴜɴᴛʀʏ**: {domain_info.country}\n"
        f"**ʀᴇɢɪsᴛʀᴀɴᴛ ᴘʜᴏɴᴇ**: {domain_info.phone}\n"
        f"**ᴇᴍᴀɪʟs**: {format_list(domain_info.emails)}\n"
        f"**ᴡʜᴏɪs sᴇʀᴠᴇʀ**: {domain_info.whois_server}\n"
    )
    return response

@app.on_message(filters.command("domain"))
async def get_domain_info(client, message):
    if len(message.command) > 1:
        domain_name = message.text.split(maxsplit=1)[1]
        domain_info = get_domain_hosting_info(domain_name)

        response = format_domain_info(domain_info) if domain_info else "Failed to retrieve domain hosting information."
    else:
        response = "Please provide a domain name after the /domain command."

    await message.reply(response)