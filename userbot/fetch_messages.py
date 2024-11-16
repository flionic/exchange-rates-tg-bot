from Token import api_id, api_hash

from telethon import TelegramClient


async def fetch_chat_messages(chat_id, limit, offset_id):
    async with TelegramClient('./userbot/yourdev', api_id, api_hash) as client:
        sum_messages = []

        async for message in client.iter_messages(chat_id, limit=limit, offset_id=offset_id):
            sender = await message.get_sender()
            sender_name = sender.first_name if sender else "Unknown"
            msg = f'{sender_name}|{message.text}|{message.date.replace(tzinfo=None)}|{message.id}'
            sum_messages.append(msg)

        return '\n'.join(sum_messages)
