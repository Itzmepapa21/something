from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Replace these values with your own
api_id = 21310924
api_hash = 'fa4c3f582286d969ab1d08449e9533e8'
bot_token = '7183078971:AAGinBsxYNnwiCvcu0X-YfL5zgiDkA74l0Q'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.forwarded & filters.private)
async def forward_handler(client, message):
    chat_id = message.forward_from_chat.id
    user_id = message.from_user.id
    
    # Check if bot is admin in the forwarded channel
    chat_info = await client.get_chat_member(chat_id, user_id)
    if chat_info.status == 'administrator':
        # Ask for the link
        await message.reply_text("Please provide the link for the button.")
        app.registered_link = chat_id
    else:
        await message.reply_text("You are not an admin in the forwarded channel.")

@app.on_message(filters.private)
async def link_handler(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if hasattr(app, 'registered_link') and user_id == app.registered_link:
        link = message.text
        await message.reply_text("Button link registered successfully.")
        
        # Edit the forwarded message in the channel
        forwarded_message = await client.get_messages(app.registered_link, message.message_id)
        buttons = []
        
        # Add the new "Dual" button
        buttons.append([InlineKeyboardButton("Dual", url=link)])
        
        # Check if there are existing buttons in the message
        if forwarded_message.reply_markup and forwarded_message.reply_markup.inline_keyboard:
            buttons += forwarded_message.reply_markup.inline_keyboard
        
        # Create InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Edit the message with the new buttons
        await forwarded_message.edit_reply_markup(reply_markup)
        
        # Clear registered link
        del app.registered_link
    else:
        await message.reply_text("You are not authorized to set the link.")

app.run()
