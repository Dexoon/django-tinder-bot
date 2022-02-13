import os
from typing import Optional

import telegram
from django.core.files import File
from telegram.error import BadRequest
from django.conf import settings
from telegram.files.file import File as TelegramFile

from .models import ChatMember


def check_chat_member(chat_member: ChatMember):
    from .dispatcher import bot
    try:
        status = bot.get_chat_member(chat_id=chat_member.chat.chat_id, user_id=chat_member.user.user_id)
    except BadRequest as e:
        print(e, chat_member.chat.chat_id, chat_member.user.user_id)
        return
    if chat_member.status != status.status:
        chat_member.status = status.status
        chat_member.save()


def download_photo_size(photo_size: telegram.PhotoSize) -> Optional[str]:
    try:
        telegram_file: TelegramFile = photo_size.get_file()
    except telegram.error.TelegramError:
        return
    _, ext = os.path.splitext(telegram_file.file_path)
    filepath = os.path.join(settings.MEDIA_ROOT, telegram_file.file_unique_id + ext)
    if not os.path.isfile(filepath):
        filepath = telegram_file.download(custom_path=filepath)
    return filepath
