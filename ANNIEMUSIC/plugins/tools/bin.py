import requests
from pyrogram import *
from pyrogram.types import *
from ANNIEMUSIC import app

@app.on_message(filters.command(["bin", "ccbin", "bininfo"], [".", "!", "/"]))
async def check_ccbin(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Please Give Me a Bin To\nGet Bin Details !</b>"
        )
    try:
        await message.delete()
    except:
        pass
    aux = await message.reply_text("<b>Checking ...</b>")
    bin = message.text.split(None, 1)[1]
    if len(bin) < 6:
        return await aux.edit("<b>❌ Wrong Bin❗...</b>")
    
    url = "https://bin-ip-checker.p.rapidapi.com/"
    querystring = {"bin": bin}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "923bca7ccdmsh620363d2a9cf295p15f78bjsnfa1040c941aa",
        "X-RapidAPI-Host": "bin-ip-checker.p.rapidapi.com"
    }
    
    try:
        response = requests.post(url, headers=headers, params=querystring)
        data = response.json()
        
        if data.get("success", False):
            bin_info = data.get("BIN", {})
            await aux.edit(f"""
<b> 𝗩𝗔𝗟𝗜𝗗 𝗕𝗜𝗡 ✅</b>

<b>┏━◆</b>
<b>┣〖🏦 ʙᴀɴᴋ</b> ⇾<tt>{bin_info.get('issuer', {}).get('name', 'N/A')}</tt>
<b>┣〖💳 ʙɪɴ</b> ⇾<tt>`{bin}`</tt>
<b>┣〖🏡 ᴄᴏᴜɴᴛʀʏ</b> ⇾<tt>{bin_info.get('country', {}).get('country', 'N/A')}</tt>
<b>┣〖🇮🇳 ғʟᴀɢ</b> ⇾<tt>{bin_info.get('country', {}).get('alpha2', 'N/A')}</tt>
<b>┣〖🧿 ɪsᴏ</b> ⇾<tt>{bin_info.get('country', {}).get('alpha3', 'N/A')}</tt>
<b>┣〖⏳ ʟᴇᴠᴇʟ</b> ⇾<tt>{bin_info.get('level', 'N/A')}</tt>
<b>┣〖🔴 ᴘʀᴇᴘᴀɪᴅ</b> ⇾<tt>{'Yes' if bin_info.get('type') == 'DEBIT' else 'No'}</tt>
<b>┣〖🆔 ᴛʏᴘᴇ</b> ⇾<tt>{bin_info.get('type', 'N/A')}</tt>
<b>┣〖ℹ️ ᴠᴇɴᴅᴏʀ</b> ⇾<tt>{bin_info.get('brand', 'N/A')}</tt>
<b>┗━━━◆</b>
""")
        else:
            await aux.edit("🚫 BIN not recognized. Please enter a valid BIN.")
    except Exception as e:
        print(e)
        await aux.edit("❌ An error occurred while fetching BIN information.")
