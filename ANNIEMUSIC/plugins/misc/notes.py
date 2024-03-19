from ANNIEMUSIC import app
from config import BOT_USERNAME
from pyrogram import filters
from ANNIEMUSIC.utils.jarvis_ban import admin_filter
from ANNIEMUSIC.mongo.notesdb import *
from ANNIEMUSIC.utils.notes_func import GetNoteMessage, exceNoteMessageSender, privateNote_and_admin_checker
from ANNIEMUSIC.utils.yumidb import user_admin
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatMemberStatus

# Command to save a note
@app.on_message(filters.command("save") & admin_filter)
@user_admin
async def save_note(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    if message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Please provide a name for the note!")

    if not message.reply_to_message and len(message.command) < 3:
        return await message.reply_text("Please provide some content for the note!")

    note_name = message.command[1]
    content, text, data_type = GetNoteMessage(message)
    
    try:
        await SaveNote(chat_id, note_name, content, text, data_type)
        await message.reply_text(f"Note '{note_name}' has been saved in {chat_title}.")
    except Exception as e:
        await message.reply_text(f"An error occurred while saving the note: {str(e)}")

# Command to retrieve a note
@app.on_message(filters.command("get") & admin_filter)
async def get_note(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply_text("Please specify the name of the note!")

    note_name = message.command[1]
    if not await isNoteExist(chat_id, note_name):
        return await message.reply_text("Note not found")

    await send_note(message, note_name)

# Regular expression to retrieve a note
@app.on_message(filters.regex(pattern=(r"^#[^\s]+")) & filters.group)
async def regex_get_note(client, message):
    chat_id = message.chat.id
    if message.from_user:
        note_name = message.text.split()[0].replace('#', '')
        if await isNoteExist(chat_id, note_name):
            await send_note(message, note_name)

# Command to toggle private notes setting
@app.on_message(filters.command("privatenotes") & filters.group)
@user_admin
async def private_notes(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply_text("Please specify 'on' or 'off'!")

    setting = message.command[1].lower()
    if setting in ['on', 'off']:
        await set_private_note(chat_id, setting == 'on')
        await message.reply_text(f"Private notes setting updated to '{setting}'.")
    else:
        await message.reply_text("Invalid setting. Please specify 'on' or 'off'!")

# Command to clear a specific note
@app.on_message(filters.command("clear") & admin_filter)
@user_admin
async def clear_note(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply_text("Please specify the name of the note!")

    note_name = message.command[1].lower()
    if await isNoteExist(chat_id, note_name):
        await ClearNote(chat_id, note_name)
        await message.reply_text(f"Note '{note_name}' has been deleted.")
    else:
        await message.reply_text("Note not found.")

# Command to clear all notes
@app.on_message(filters.command("clearall") & admin_filter)
async def clear_all_notes(client, message):
    owner_id = message.from_user.id
    chat_id = message.chat.id
    chat_title = message.chat.title
    user = await client.get_chat_member(chat_id, owner_id)
    if user.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only the owner can use this command!")

    note_list = await NoteList(chat_id)
    if not note_list:
        return await message.reply_text(f"No notes found in {chat_title}.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Delete all notes', callback_data=f'clearallnotes_clear_{owner_id}_{chat_id}')],
        [InlineKeyboardButton(text='Cancel', callback_data=f'clearallnotes_cancel_{owner_id}')]
    ])
    await message.reply_text(
        f"Are you sure you want to delete **ALL** notes in {chat_title}? This action is irreversible.",
        reply_markup=keyboard
    )

# Callback query handler for clearing all notes
@app.on_callback_query(filters.regex("^clearallnotes_"))
async def clear_all_callback(client, callback_query: CallbackQuery):
    query_data = callback_query.data.split('_')[1]
    owner_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    if owner_id == user_id:
        if query_data == 'clear':
            chat_id = int(callback_query.data.split('_')[3])
            await ClearAllNotes(chat_id)
            await callback_query.answer("All notes have been deleted.")
        elif query_data == 'cancel':
            await callback_query.answer("Cancelled.")
    else:
        await callback_query.answer("Only admins can execute this command!")

# Command to list all saved notes
@app.on_message(filters.command(['notes', 'saved']) & filters.group)
async def list_notes(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    notes_list = await NoteList(chat_id)
    if notes_list:
        note_header = f"List of notes in {chat_title}:\n"
        note_list_str = '\n'.join([f" • `#{note}`" for note in notes_list])
        await message.reply_text(
            f"{note_header}{note_list_str}\nYou can retrieve these notes using `/get notename` or `#notename`.",
            quote=True
        )
    else:
        await message.reply_text(f"No notes found in {chat_title}.", quote=True)

# Function to send a note message
async def send_note(message, note_name):
    chat_id = message.chat.id
    content, text, data_type = await GetNote(chat_id, note_name)
    private_note, allow = await privateNote_and_admin_checker(message, text)
    if allow:
        if private_note is None or private_note == await is_pnote_on(chat_id):
            if private_note:
                await private_note_button(message, chat_id, note_name)
            else:
                await exceNoteMessageSender(message, note_name)

# Function to send a private note button
async def private_note_button(message, chat_id, note_name):
    private_note_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Click me!', url=f'http://t.me/{BOT_USERNAME}?start=note_{chat_id}_{note_name}')]
    ])
    await message.reply_text(
        text=f"Tap here to view '{note_name}' in your private chat.",
        reply_markup=private_note_button
    )
