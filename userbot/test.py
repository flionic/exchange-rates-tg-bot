from Token import api_id, api_hash

from telethon import TelegramClient

# The first parameter is the .session file name (absolute paths allowed)
with TelegramClient('yourdev', api_id, api_hash) as client:
    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))
