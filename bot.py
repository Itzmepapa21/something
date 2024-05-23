import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your **actual API credentials** (never share publicly)
API_ID = 21310924
API_HASH = 'fa4c3f582286d969ab1d08449e9533e8'
BOT_TOKEN = '7183078971:AAGinBsxYNnwiCvcu0X-YfL5zgiDkA74l0Q'
async def edit_post(client, message):
    """
    Edits a post in a private chat or public channel (if permissions allow).

    Args:
        client (pyrogram.Client): The Pyrogram client instance.
        message (pyrogram.types.Message): The incoming message triggering the edit.
    """

    if len(message.text.split()) >= 3:
        command, post_link, dual_link = message.text.split(maxsplit=2)
        if command == "/edit":
            try:
                if "/" in post_link:  # Likely a public channel link
                    chat = await client.get_chat(chat_id=post_link)
                    message_id = int(post_link.split("/")[-1])

                    # Check edit_message permission for public channels
                    member = await chat.get_member(message.from_user.id)
                    if not member.can_edit_message(message_id):
                        await message.reply("Insufficient permissions to edit messages in this channel.")
                        return

                    post = await client.get_messages(chat.id, message_ids=message_id)
                else:  # Assuming private chat
                    chat_id = message.chat.id
                    message_id = message.message_id

                    # Check edit_message permission for private chats
                    chat_member = await client.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)
                    if not chat_member.can_edit_message(message_id):
                        await message.reply("Insufficient permissions to edit messages in this chat.")
                        return

                    post = await client.get_messages(chat_id, message_ids=message_id)

                message_id = post.message_id
                post_buttons = post.reply_markup.inline_keyboard if post.reply_markup else None
                dual_button = [InlineKeyboardButton("Dual", url=dual_link)]
                new_buttons = [dual_button] + post_buttons if post_buttons else [dual_button]

                await client.edit_message_reply_markup(
                    chat_id=chat_id,
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

# Initialize and run the Pyrogram client (replace "..." with actual credentials)
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app.run(edit_post)
        
