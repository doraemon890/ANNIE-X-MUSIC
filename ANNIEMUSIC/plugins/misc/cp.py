from ANNIEMUSIC import ANNIEMUSIC as app
from pyrogram import Client, filters



async def delete_links(message):
    if any(link in message.text for link in ["http", "https", "www."]):
        await message.delete()

@app.on_message(filters.group & filters.text & ~filters.me)
async def handle_messages(client, message):
    await delete_links(message)

@app.on_edited_message(filters.group & filters.text & ~filters.me)
async def handle_edited_messages(client, edited_message):
    await delete_links(edited_message)


#---------------------------------------------------------------------------
keywords_to_delete = ["NCERT", "XII", "page", "Ans", "meiotic", "divisions", "System.in", "Scanner", "void", "nextInt"]
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
@app.on_message(filters.group & filters.text & ~filters.me)
async def delete_links(client, message):
    if any(keyword in message.text for keyword in keywords_to_delete) and len(message.text.split()) > 20:
        await message.delete()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

@app.on_edited_message(filters.group & filters.text & ~filters.me)
async def delete_edited_links(client, edited_message):
    if any(keyword in edited_message.text for keyword in keywords_to_delete) and len(edited_message.text.split()) > 20:
        await edited_message.delete()
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

@app.on_message(filters.group & filters.text & ~filters.me)
async def delete_long_messages(client, message):
    if len(message.text.split()) >= 20:
        await message.delete()
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
@app.on_edited_message(filters.group & filters.text & ~filters.me)
async def delete_edited_long_messages(client, edited_message):
    if len(edited_message.text.split()) >= 20:
        await edited_message.delete()


#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
