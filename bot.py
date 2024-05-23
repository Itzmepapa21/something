from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your API_ID, API_HASH, and BOT_TOKEN


# Define your admin user(s) IDs
admin_ids = [7030439873, 6072442458, 987654321]

API_ID = 21310924
API_HASH = 'fa4c3f582286d969ab1d08449e9533e8'
BOT_TOKEN = '7183078971:AAGinBsxYNnwiCvcu0X-YfL5zgiDkA74l0Q'

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.user(admin_ids))
async def edit_post(client, message):
    if len(message.text.split()) >= 3:
        command, post_link, dual_link = message.text.split(maxsplit=2)
        if command == "/edit":
            try:
                # No need to extract chat ID from link anymore
                post = await client.get_messages(chat_id=None, message_links=post_link)
                message_id = post.message_id
                post_buttons = post.reply_markup.inline_keyboard if post.reply_markup else None
                dual_button = [InlineKeyboardButton("Dual", url=dual_link)]
                new_buttons = [dual_button] + post_buttons if post_buttons else [dual_button]
                await client.edit_message_reply_markup(
                    chat_id=post.chat.id,  # Directly use chat.id from retrieved post
                    message_id=message_id,
                    reply_markup=InlineKeyboardMarkup(new_buttons)
                )
                await message.reply("Post edited successfully!")
            except Exception as e:
                await message.reply(f"Error editing post: {e}")
        else:
            await message.reply("Invalid command. Please use /edit post_link dual_link")
    else:
        await message.reply("Invalid command. Please use /edit post_link dual_link")

app.run()
