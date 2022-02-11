import datetime

from django.utils import timezone
from django.conf import settings
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.models import User, Chat
from sesame.utils import get_query_string


def private_command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    text = static_text.private_start.format(link=f"\nhttps://{settings.URL}/{get_query_string(u)}")

    update.message.reply_text(text=text)


def public_command_start(update: Update, context: CallbackContext) -> None:
    from tgbot.dispatcher import TELEGRAM_BOT_USERNAME
    u, created = User.get_user_and_created(update, context)
    c, created = Chat.get_chat_and_created(update, context)
    text = static_text.public_start.format(bot_username=TELEGRAM_BOT_USERNAME)

    update.message.reply_text(text=text)
