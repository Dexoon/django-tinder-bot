from __future__ import annotations

import asyncio
from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from django.contrib.auth.models import AbstractUser

from dtb.settings import DEBUG
from .handlers.utils.info import extract_user_data_from_update, extract_chat_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(AbstractUser, CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb, unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    crushes = models.ManyToManyField("self", symmetrical=False, through='Like', related_name='followers')

    class Meta:
        ordering = ('user_id',)

    def __str__(self):
        return self.tg_str

    def send_message(self, **kwargs):
        from .dispatcher import bot
        bot.send_message(chat_id=self.user_id, **kwargs)

    def mutual_notify(self, another_user):
        self.send_message(text=f"Это мэтч! {another_user.html_str}", parse_mode='HTML')

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    @property
    def tg_str(self) -> str:
        if self.tg_username:
            return f'@{self.username}'
        return self.full_name

    @property
    def long_name(self):
        if self.tg_username:
            return f'@{self.username} {self.full_name}'
        return self.full_name

    @property
    def tg_username(self) -> str | None:
        try:
            int(self.username)
            return None
        except ValueError:
            return self.username
        except TypeError:
            return None

    @property
    def html_str(self) -> str:
        if username := self.tg_username:
            return f'@{username}'
        name = f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"
        return f"<a href=\"tg://user?id={self.user_id}\">{name}</a>"

    def like(self, crush: User):
        if self != crush:
            l, created = Like.objects.get_or_create(from_user=self, to_user=crush)
            return l.is_mutual()
        return None

    def unlike(self, crush):
        if like := Like.objects.filter(from_user=self, to_user=crush).first():
            like.delete()
        return True


class Chat(CreateUpdateTracker):
    chat_id = models.BigIntegerField(primary_key=True)  # telegram_id
    title = models.CharField(max_length=256, **nb)

    class TYPE(models.TextChoices):
        SENDER: str = 'sender'
        PRIVATE: str = 'private'
        GROUP: str = 'group'
        SUPERGROUP: str = 'supergroup'
        CHANNEL: str = 'channel'

    type = models.CharField(max_length=16, choices=TYPE.choices, default=TYPE.PRIVATE)
    username = models.CharField(max_length=256, **nb)
    users = models.ManyToManyField(User, through='ChatMember', related_name='chats')

    @classmethod
    def get_chat_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_chat_data_from_update(update)
        print(data)
        try:
            c, created = cls.objects.update_or_create(chat_id=data["chat_id"], defaults=data)
        except Exception as e:
            print(e)
        print(c, created)
        return c, created

    def __str__(self):
        return self.title


@receiver(pre_save, sender=Chat)
def get_chat_info(sender, instance, *args, **kwargs):
    from .dispatcher import bot
    chat = bot.get_chat(chat_id=instance.chat_id or f"@{instance.username}")
    instance.chat_id = chat.id
    instance.username = chat.username
    instance.title = chat.title
    instance.type = chat.type


@receiver(post_save, sender=Chat)
def get_chat_members(sender, instance, created, *args, **kwargs):
    if instance.type in [instance.TYPE.GROUP, instance.TYPE.SUPERGROUP]:
        from .tasks import get_chat_members as task_get_chat_members
        task_get_chat_members.delay(instance.chat_id)


class ChatMember(CreateUpdateTracker):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['chat', 'user']

    class STATUS(models.TextChoices):
        OWNER = 'creator'
        ADMINISTRATOR = 'administrator'
        MEMBER = 'member'
        RESTRICTED = 'restricted'
        LEFT = 'left'
        BANNED = 'kicked'

    status = models.CharField(max_length=16, choices=STATUS.choices, default=STATUS.MEMBER)

    def __str__(self):
        return f'{self.status}: {self.chat} {self.user}'


class Like(CreateUpdateTracker):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='got_likes')

    class Meta:
        unique_together = ['from_user', 'to_user']

    def is_mutual(self) -> bool:
        if self.from_user == self.to_user:
            return False
        return self.from_user in self.to_user.crushes.all()


@receiver(post_save, sender=Like)
def notify_mutual(sender, instance, created, *args, **kwargs):
    if created and instance.is_mutual():
        instance.from_user.mutual_notify(instance.to_user)
        instance.to_user.mutual_notify(instance.from_user)
