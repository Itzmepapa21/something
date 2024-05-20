import telethon
from telethon.tl.functions.messages import EditMessageReplyMarkupRequest, EditMessageTextRequest
from telethon.tl.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Replace with your Telegram API details
API_ID = int('21310924')
API_HASH = 'fa4c3f582286d969ab1d08449e9533e8'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

client = telethon.TelegramClient('session_name', API_ID, API_HASH)

async def main():
    @client.on(telethon.events.NewMessage(pattern='/start'))
    async def handle_start(event: Message):
        if not event.is_private:
            await event.respond('This bot can only be used in private chats.')
            return

        admin_channels = await get_admin_channels(client)

        if not admin_channels:
            await event.respond('You are not an admin in any channels.')
            return

        channel_buttons = [
            InlineKeyboardButton(channel['title'], callback_data=f'channel_{channel["id"]}')
            for channel in admin_channels
        ]
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(*channel_buttons)

        await event.respond('Select a channel:', buttons=markup)

    @client.on(telethon.events.CallbackQuery)
    async def handle_callback(event: telethon.events.CallbackQuery):
        channel_id = int(event.data.split('_')[1])

        await event.answer()

        action_buttons = [
            InlineKeyboardButton('Post Editing', callback_data='edit_post'),
            InlineKeyboardButton('Post Forward', callback_data='forward_post'),
        ]
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(*action_buttons)

        await event.edit(text='What do you want to do?', buttons=markup)

    @client.on(telethon.events.CallbackQuery)
    async def handle_action(event: telethon.events.CallbackQuery):
        if event.data == 'edit_post':
            await event.answer()
            await event.edit(text='Send the original post link for editing.')

            @client.on(telethon.events.NewMessage(pattern=r'https?://t.me/\S+/(\d+)'))
            async def handle_post_link(event: Message):
                post_link = event.text
                await client.delete_messages(event.chat_id, event.message.id)  # Delete link message

                await event.respond('Send the "Dual{Eng+Jap}" link.')

                @client.on(telethon.events.NewMessage(pattern=r'https?://\S+'))
                async def handle_dual_link(event: Message):
                    dual_link = event.text
                    await client.delete_messages(event.chat_id, event.message.id)  # Delete link message

                    try:
                        # Attempt to edit the post, replacing "Japanese [English Subtitles]" with "Dual{Eng+Jap}" if found
                        edited_message = await edit_post(client, channel_id, post_link, dual_link)

                        if edited_message:
                            await event.respond('Post edited successfully!')

                            # Extract existing buttons from the original post (if any)
                            original_buttons = None
                            original_message = await client.get_messages(channel_id, ids=int(post_link.split('/')[-1]))
                            if original_message and original_message.buttons:
                                original_buttons = original_message.buttons

                            # Create and add the "Dual" button with the provided link
                            dual_button = InlineKeyboardButton('Dual', url=dual_link)
                            new_buttons = [dual_button]

                            if original_buttons:
                                new_buttons.extend(original_buttons)

                            await edit_message_buttons(client, channel_id, edited_message.id, new_buttons)
                        else:
                            await event.respond('Could not edit the post. Make sure the link is valid and you have permission to edit.')
                    except Exception as e:
                        await event.respond(f'An error occurred: {str(e)}')

        elif event.data == 'forward_post':
            await event.answer()
            await event.edit(text='Share the post you want to forward.')

            @client.on(telethon.events.Message)
            async def handle_forward(event: Message):
                if not event.is_forwarded:
                    await event.respond('Please share a forwarded post.')
                    return

                forwarded_message = event.message.fwd_from

                try:
                    await client.forward_messages(channel_id, forwarded_message.chat_id, forwarded_message.id,
                                                  silent=True, background=True)  # Forward silently in the background

                    # Check if the forwarded message has buttons and extract them if so
                    forwarded_buttons = None
                    if forwarded_message.buttons:
                        forwarded_buttons = forwarded_message.buttons

                    # Forward with "Forwarded" tag if available (Telethon v1.8+)
                    if hasattr(telethon.tl.types.Message, 'forwarded'):
                        forwarded_post = await client.get_messages(channel_id, ids=forwarded_message.id)
                        if forwarded_post and forwarded_post.forwarded:
                            await event.respond('Forwarded successfully (with "Forwarded" tag).')
                        else:
                            await event.respond('Forwarded successfully.')
                    else:
                        await event.respond('Forwarded successfully.')

                    # If the forwarded message has buttons, add them to the forwarded post in the channel
                    if forwarded_buttons:
                        await edit_message_buttons(client, channel_id, forwarded_message.id, forwarded_buttons)
                except Exception as e:
                    await event.respond(f'An error occurred: {str(e)}')

async def get_admin_channels(client: telethon.TelegramClient) -> list:
    """
    Retrieves a list of channels where the bot is an admin.
    """
    admin_channels = []
    async for dialog in client.iter_dialogs(chat_type='channel'):
        if dialog.chat.creator or dialog.chat.admin_rights:
            admin_channels.append({
                'id': dialog.chat.id,
                'title': dialog.chat.title,
            })
    return admin_channels

async def edit_post(client: telethon.TelegramClient, channel_id: int, post_link: str, dual_link: str) -> Message:
    """
    Attempts to edit the post at the given link, replacing "Japanese [English Subtitles]" with "Dual{Eng+Jap}".

    Returns the edited message object if successful, None otherwise.
    """
    try:
        message_id = int(post_link.split('/')[-1])
        entity = await client.get_entity(channel_id)
        message = await client.get_messages(entity, ids=message_id)

        if message.empty:
            return None  # Post not found

        new_text = message.text.replace('Japanese [English Subtitles]', 'Dual{Eng+Jap}', 1)
        await client(EditMessageText(entity, message_id, message=new_text))
        return await client.get_messages(entity, ids=message_id)
    except Exception:
        return None

async def edit_message_buttons(client: telethon.TelegramClient, channel_id: int, message_id: int, buttons: list):
    """
    Edits the buttons of the post with the given ID in the specified channel.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await client(EditMessageReplyMarkup(channel_id, message_id, reply_markup=markup))

if __name__ == '__main__':
    client.start(main)
    client.run_until_disconnected()
  
          
