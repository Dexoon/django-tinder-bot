#!/bin/bash
python manage.py migrate
python manage.py set_webhook
python manage.py set_commands
exec "$@"
