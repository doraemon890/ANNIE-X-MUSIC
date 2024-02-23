from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ANNIEMUSIC import app
from config import BOT_USERNAME

start_txt = """**
✪ ωεℓ¢σмє ƒσя jคяv¡ร яєρσѕ ✪
 
 ➲ ᴀʟʟ ʀᴇᴘᴏ ᴇᴀsɪʟʏ ᴅᴇᴘʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ᴇʀʀᴏʀ ✰
 
 ➲ ɴᴏ ʜᴇʀᴏᴋᴜ ʙᴀɴ ɪssᴜᴇ ✰
 
 ➲ ɴᴏ ɪᴅ ʙᴀɴ ɪssᴜᴇ ✰
 
 ➲ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏs ✰
 
 ➲ ʀᴜɴ 24x7 ʟᴀɢ ғʀᴇᴇ ᴡɪᴛʜᴏᴜᴛ sᴛᴏᴘ ✰
 
 ► ɪғ ʏᴏᴜ ғᴀᴄᴇ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ᴛʜᴇɴ sᴇɴᴅ ss
**"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
     
            [ 
            InlineKeyboardButton("𝗔𝗗𝗗 𝗠𝗘", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
            ],
     
            [
             InlineKeyboardButton("𝗛𝗘𝗟𝗣", url="https://t.me/BWANDARLOK"),
             InlineKeyboardButton("𝗢𝗪𝗡𝗘𝗥", url="https://t.me/jarvis2O"),
             ],
     
             [
             InlineKeyboardButton("𝗟𝗜𝗩𝗘 𝗖𝗖", url="https://t.me/OXY474_STORE"),
             ],
     
             [
             InlineKeyboardButton("𝗦𝗧𝗥𝗜𝗡𝗚𝗕𝗢𝗧", url=f"https://github.com/doraemon890/JARVIS-X-SESSION"),            
             InlineKeyboardButton("︎𝗠𝗨𝗦𝗜𝗖", url=f"https://github.com/doraemon890/ANNIE-X-MUSIC"),
             ],
     
             [
             InlineKeyboardButton("𝐄𝐕𝐈𝐋", url=f"https://github.com/doraemon890/JARVIS-X-EVIL"),
             InlineKeyboardButton("𝐁𝐀𝐍 𝐀𝐋𝐋", url=f"https://github.com/doraemon890/jarvis-ban-all"),
             ],
     
             [
             InlineKeyboardButton("𝐀𝐋𝐋 𝐁𝐎𝐓𝐒", url=f"https://t.me/CDX_WORLD"),
             InlineKeyboardButton("𝐁𝐖𝐀𝐍𝐃𝐀𝐑𝐋𝐎𝐊", url=f"https://t.me/BWANDARLOK"),
             ],
     
              [
              InlineKeyboardButton("𝐆𝐈𝐓𝐇𝐔𝐁 𝐏𝐑𝐎𝐅𝐈𝐋𝐄", url=f"https://github.com/doraemon890"),
              InlineKeyboardButton("𝐃𝐎𝐑𝐀𝐄𝐌𝐎𝐍♡︎", url=f"https://t.me/Doraemon890"),
              ],
     
              [
              InlineKeyboardButton("𝐏𝐘𝐑𝐎𝐍𝐄", url=f"https://github.com/doraemon890/JARVIS-X-PYRON"),
              InlineKeyboardButton("𝗔𝗟 𝗦𝗣𝗔𝗠 𝗕𝗢𝗧", url=f"https://github.com/doraemon890/JARVIS-X-SPAM"),
              ]
       ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://telegra.ph/file/58afe55fee5ae99d6901b.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
