from ... import *
from pyrogram import *
from pyrogram.types import *


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
    try:
        resp = await api.bininfo(bin)
        await aux.edit(f"""
<b> 𝗩𝗔𝗟𝗜𝗗 𝗕𝗜𝗡 ✅</b>

<b>┏━◆</b>
<b>┣〖🏦 ʙᴀɴᴋ</b> ⇾<tt>{resp.bank}</tt>
<b>┣〖💳 ʙɪɴ</b> ⇾<tt>`{resp.bin}`</tt>
<b>┣〖🏡 ᴄᴏᴜɴᴛʀʏ</b> ⇾<tt>{resp.country}</tt>
<b>┣〖🇮🇳 ғʟᴀɢ</b> ⇾<tt>{resp.flag}</tt>
<b>┣〖🧿 ɪsᴏ</b> ⇾<tt>{resp.iso}</tt>
<b>┣〖⏳ ʟᴇᴠᴇʟ</b> ⇾<tt>{resp.level}</tt>
<b>┣〖🔴 ᴘʀᴇᴘᴀɪᴅ</b> ⇾<tt>{resp.prepaid}</tt>
<b>┣〖🆔 ᴛʏᴘᴇ</b> ⇾<tt>{resp.type}</tt>
<b>┣〖ℹ️ ᴠᴇɴᴅᴏʀ</b> ⇾<tt>{resp.vendor}</tt>
<b>┗━━━◆</b>
"""
        )
    except:
        return await aux.edit(f"""
🚫 BIN not recognized. Please enter a valid BIN.""")
