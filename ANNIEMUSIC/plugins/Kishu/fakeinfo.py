import requests
from ANNIEMUSIC import app as Checker
from pyrogram import filters

VALID_COUNTRY_CODES = [
    "AU", "BR", "CA", "CH", "DE", "DK", "ES", "FI", "FR", "GB",
    "IE", "IR", "NO", "NL", "NZ", "TR", "US"
]

@Checker.on_message(filters.command("fake"))
async def address(_, message):
    message_text = message.text.strip()
    words = message_text.split()
    
    if len(words) > 1:
        query = words[1].strip().upper()
        
        if query in VALID_COUNTRY_CODES:
            url = f"https://randomuser.me/api/?nat={query}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "results" in data:
                    user_data = data["results"][0]

                    name = f"{user_data['name']['title']} {user_data['name']['first']} {user_data['name']['last']}"
                    address = f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}"
                    city = user_data['location']['city']
                    state = user_data['location']['state']
                    country = user_data['location']['country']
                    postal = user_data['location']['postcode']
                    email = user_data['email']
                    phone = user_data['phone']
                    picture_url = user_data['picture']['large']

                    caption = f"""
﹝⌬﹞**ɴᴀᴍᴇ** ⇢ {name}
﹝⌬﹞**ᴀᴅᴅʀᴇss** ⇢ {address}
﹝⌬﹞**ᴄᴏᴜɴᴛʀʏ** ⇢ {country}
﹝⌬﹞**ᴄɪᴛʏ** ⇢ {city}
﹝⌬﹞**sᴛᴀᴛᴇ** ⇢ {state}
﹝⌬﹞**ᴘᴏsᴛᴀʟ** ⇢ {postal}
﹝⌬﹞**ᴇᴍᴀɪʟ** ⇢ {email}
﹝⌬﹞**ᴘʜᴏɴᴇ** ⇢ {phone}
                    """

                    await message.reply_photo(photo=picture_url, caption=caption)
                else:
                    await message.reply_text("ᴏᴏᴘs ɴᴏᴛ ғᴏᴜɴᴅ ᴀɴʏ ᴀᴅᴅʀᴇss.")
            else:
                await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴅᴀᴛᴀ ғʀᴏᴍ ᴛʜᴇ API.")
        else:
            await message.reply_text(f"ɪɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ. ᴘʟᴇᴀsᴇ ᴜsᴇ ᴏɴᴇ ᴏғ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ: {', '.join(VALID_COUNTRY_CODES)}")
    else:
        await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.")
