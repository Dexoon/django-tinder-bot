from django.core.management.base import BaseCommand, CommandError
from ...dispatcher import bot, set_up_commands
from django.conf import settings


class Command(BaseCommand):
    help = 'Set default webhook address'

    def handle(self, *args, **options):
        try:
            set_up_commands(bot)
            print(f"Commands was set")
        except:
            print(f"Commands was not set")
