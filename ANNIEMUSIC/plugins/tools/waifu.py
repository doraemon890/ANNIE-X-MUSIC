import requests
from pyrogram import filters
from ANNIEMUSIC import app

# Waifu image functionality
@app.on_message(filters.command("waifu"))
async def waifu_command_handler(_, message):
    try:
        tags = ['maid']  # You can customize the tags as needed
        waifu_data = get_waifu_data(tags)

        if waifu_data and 'images' in waifu_data:
            first_image = waifu_data['images'][0]
            image_url = first_image['url']
            await message.reply_photo(image_url)
        else:
            await message.reply_text("No waifu found with the specified tags.")

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply_text(f"An error occurred: {e}")

# Helper function to get waifu data
def get_waifu_data(tags):
    params = {
        'included_tags': tags,
        'height': '>=2000'
    }

    response = requests.get('https://api.waifu.im/search', params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None
