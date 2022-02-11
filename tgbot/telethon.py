from django.conf import settings
from telethon import TelegramClient

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Chat, User, ChatMember
client = TelegramClient("bot", settings.API_ID, settings.API_HASH)


def get_chat_members(chat_id) -> list['User']:
    client.start(bot_token=settings.TELEGRAM_TOKEN)
    from .models import User, ChatMember
    users: list[User] = []
    members = client.iter_participants(chat_id)
    for member in members:
        if not member.bot:
            print(member)
            user, created = User.objects.update_or_create(user_id=member.id, defaults={
                'username': member.username, 'first_name': member.first_name, 'last_name': member.last_name
            })
            ChatMember.objects.get_or_create(chat_id=chat_id, user=user)
            users += [user]
    return users
