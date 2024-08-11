from pyrogram import Client, filters
from nekosbest import Client as NekoClient
from ANNIEMUSIC import app

# Initialize the nekosbest client
neko_client = NekoClient()

# Define available commands and their responses
commands = {
    "punch": {"emoji": "💥", "text": "punched"},
    "slap": {"emoji": "😒", "text": "slapped"},
    "hug": {"emoji": "🤗", "text": "hugged"},
    "bite": {"emoji": "😈", "text": "bit"},
    "kiss": {"emoji": "😘", "text": "kissed"},
    "highfive": {"emoji": "🙌", "text": "high-fived"},
    "shoot": {"emoji": "🔫", "text": "shot"},
    "dance": {"emoji": "💃", "text": "danced"},
    "kick": {"emoji": "👟", "text": "kicked"},
    "happy": {"emoji": "😊", "text": "was happy"},
    "baka": {"emoji": "😡", "text": "called you a baka"},
    "pat": {"emoji": "👋", "text": "patted"},
    "nod": {"emoji": "👍", "text": "nodded"},
    "nope": {"emoji": "👎", "text": "said nope"},
    "cuddle": {"emoji": "🤗", "text": "cuddled"},
    "feed": {"emoji": "🍴", "text": "fed"},
    "bored": {"emoji": "😴", "text": "was bored"},
    "nom": {"emoji": "😋", "text": "nommed"},
    "yawn": {"emoji": "😪", "text": "yawned"},
    "facepalm": {"emoji": "🤦", "text": "facepalmed"},
    "tickle": {"emoji": "😆", "text": "tickled"},
    "yeet": {"emoji": "💨", "text": "yeeted"},
    "think": {"emoji": "🤔", "text": "thought"},
    "blush": {"emoji": "😊", "text": "blushed"},
    "smug": {"emoji": "😏", "text": "was smug"},
    "wink": {"emoji": "😉", "text": "winked"},
    "peck": {"emoji": "😘", "text": "pecked"},
    "smile": {"emoji": "😄", "text": "smiled"},
    "wave": {"emoji": "👋", "text": "waved"},
    "poke": {"emoji": "👉", "text": "poked"},
    "stare": {"emoji": "👀", "text": "stared"},
    "shrug": {"emoji": "🤷", "text": "shrugged"},
    "sleep": {"emoji": "😴", "text": "slept"},
    "lurk": {"emoji": "👤", "text": "lurking"}
}

# Function to get animation URL
async def get_animation(animation_type):
    try:
        result = await neko_client.get_image(animation_type)
        return result.url
    except Exception as e:
        print(f"Error: {e}")
        return None

# Command handler
@app.on_message(filters.command(list(commands.keys())) & ~filters.forwarded & ~filters.via_bot)
async def animation_command(client, message):
    command = message.command[0].lower()
    if command in commands:
        gif_url = await get_animation(command)
        if gif_url:
            sender = message.from_user.mention(style='markdown')
            target = sender if not message.reply_to_message else message.reply_to_message.from_user.mention(style='markdown')
            msg = f"{sender} {commands[command]['text']} {target}! {commands[command]['emoji']}"
            await message.reply_animation(animation=gif_url, caption=msg)
        else:
            await message.reply_text("Couldn't retrieve the animation. Please try again.")
    else:
        await message.reply_text("Command not available.")