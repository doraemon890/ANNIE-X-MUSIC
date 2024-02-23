from ANNIEMUSIC import app as bot
from config import BOT_USERNAME
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

whisper_db = {}

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("●ᥫᩣ Sᴛᴀʀᴛ Wʜɪsᴘᴇʀ", switch_inline_query_current_chat="")]])

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="⦿ Wʜɪsᴘᴇʀ ⦿",
                description=f"@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(f"⦿ Usᴀɢᴇ:\n\n@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]"),
                thumb_url="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                reply_markup=switch_btn
            )
        ]
    else:
        try:
            user_id = data.split()[0]
            msg = data.split(None, 1)[1]
            user = await _.get_users(user_id)
            
            whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("❥ Wʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}")]])
            one_time_whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("☞ Oɴᴇ-Tɪᴍᴇ Wʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one")]])
            
            mm = [
                InlineQueryResultArticle(
                    title="⦿ Wʜɪsᴘᴇʀ ⦿",
                    description=f"Sᴇɴᴅ A Wʜɪsᴘᴇʀ Tᴏ {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"⦿ Yᴏᴜ Aʀᴇ Sᴇɴᴅɪɴɢ A Wʜɪsᴘᴇʀ Tᴏ {user.first_name}.\n\nTʏᴘᴇ Uʀ Mᴇssᴀɢᴇ/Sᴇɴᴛᴇɴᴄᴇ."),
                    thumb_url="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                    reply_markup=whisper_btn
                ),
                InlineQueryResultArticle(
                    title="➤ Oɴᴇ-Tɪᴍᴇ Wʜɪsᴘᴇʀ",
                    description=f"Sᴇɴᴅ A Oɴᴇ-Tɪᴍᴇ Wʜɪsᴘᴇʀ Tᴏ {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"☞ Yᴏᴜ Aʀᴇ Sᴇɴᴅɪɴɢ A Oɴᴇ-Tɪᴍᴇ Wʜɪsᴘᴇʀ Tᴏ {user.first_name}.\n\nTʏᴘᴇ Uʀ Mᴇssᴀɢᴇ/Sᴇɴᴇᴛᴇɴᴄᴇ."),
                    thumb_url="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                    reply_markup=one_time_whisper_btn
                )
            ]
            
            whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
        except Exception as e:
            mm = [
                InlineQueryResultArticle(
                    title="⦿ Wʜɪsᴘᴇʀ ⦿",
                    description="Iɴᴠᴀʟɪᴅ Usᴇʀɴᴀᴍᴇ ᴏʀ Iᴅ!",
                    input_message_content=InputTextMessageContent("ɪɴᴠᴀʟɪᴅ Usᴇʀɴᴀᴍᴇ ᴏʀ Iᴅ!"),
                    thumb_url="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
                    reply_markup=switch_btn
                )
            ]
    
    results.append(mm)
    return results



@bot.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 1983816571]:
        try:
            await _.send_message(from_user, f"{query.from_user.mention} Is Tʀʏɪɴɢ Tᴏ Oᴘᴇɴ Uʀ Wʜɪsᴘᴇʀ.")
        except Unauthorized:
            pass
        
        return await query.answer("Tʜɪs Wʜɪsᴘᴇʀ Is Nᴏᴛ Fᴏʀ Yᴏᴜ 𖣘︎", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        msg = whisper_db[search_msg]
    except:
        msg = "𖣘︎ Eʀʀᴏʀ!\n\nWʜɪsᴘᴇʀ Hᴀs Bᴇᴇɴ Dᴇʟᴇᴛᴇᴅ Fʀᴏᴍ Tʜᴇ Dᴀᴛᴀʙᴀsᴇ!"
    
    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("Gᴏ Iɴʟɪɴᴇ ➻", switch_inline_query_current_chat="")]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text("➤ Wʜɪsᴘᴇʀ Hᴀs Bᴇᴇɴ Rᴇᴀᴅ!\n\nPʀᴇss Tʜᴇ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Tᴏ Sᴇɴᴅ A Wʜɪsᴘᴇʀ!", reply_markup=SWITCH)


async def in_help():
    answers = [
        InlineQueryResultArticle(
            title="⦿ Whisper ⦿",
            description=f"@Annie_X_music_bot [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(f"**❍ Usage:**\n\n@Annie_X_music_bot (Target Username or ID) (Your Message).\n\n**Example:**\n@Annie_X_music_bot @username I Wanna Phuck You"),
            thumb_url="https://telegra.ph/file/2c6d1a6f78eba6199933a.jpg",
            reply_markup=switch_btn
        )
    ]
    return answers


@bot.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)
                                               
