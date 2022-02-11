from telegram.error import BadRequest

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
