from django.core.management.base import BaseCommand, CommandError
from ...dispatcher import bot
from django.conf import settings


class Command(BaseCommand):
    help = 'Set default webhook address'

    def handle(self, *args, **options):
        url = f"https://{settings.URL}/webhook/telegram/{settings.SECRET}/"
        try:
            bot.set_webhook(url=url)
            print(f"Webhook set on {url}")
        except:
            print(f"Webhook was not set on {url}")
