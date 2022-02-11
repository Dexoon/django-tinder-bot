import logging
import os
import sys
import environ

import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load env variables from file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default='x%#3&%giwv8f0+%r946en7z&d@9*rc$sl0qoql56xr%bh^w2mj')

DEBUG = env('DEBUG', default=False)
if DEBUG:
    environ.Env.read_env(os.path.join(BASE_DIR, 'uuid', '.env.uuid'))

ALLOWED_HOSTS = ["*", ]  # since Telegram uses a lot of IPs for webhooks

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'django_celery_beat',

    # local apps
    'tgbot.apps.TgbotConfig',
    'webpack_loader',
]
if DEBUG:
    INSTALLED_APPS.extend(('debug_toolbar',
                           'django_extensions',))

AUTHENTICATION_BACKENDS = ["sesame.backends.ModelBackend"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "sesame.middleware.AuthenticationMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
]
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

AUTH_USER_MODEL = 'tgbot.User'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'dtb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dtb.wsgi.application'
ASGI_APPLICATION = 'dtb.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
POSTGRES_USER = env('POSTGRES_USER', default='')
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD', default='')
DATABASE_HOST = env('DATABASE_HOST', default='db')
POSTGRES_DB = env('POSTGRES_DB', default='django_db')
DATABASES = {
    'default': env.db('DATABASE', default=f"psql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:5432/{POSTGRES_DB}")
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "tgbot/static"),
        os.path.join(BASE_DIR, "react-modules/static"),
    ]

# -----> CELERY
REDIS_URL = env('REDIS_URL', default='redis://redis:6379')
BROKER_URL = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_DEFAULT_QUEUE = 'default'

# -----> TELEGRAM
SECRET = env("SECRET", default='abcdef12345')
TELEGRAM_TOKEN = env("TELEGRAM_TOKEN", default=None)
if TELEGRAM_TOKEN is None:
    logging.error(
        "Please provide TELEGRAM_TOKEN in .env file.\n"
        "Example of .env file: https://github.com/ohld/django-telegram-bot/blob/main/.env_example"
    )
    sys.exit(1)

UUID = env('UUID', default='')
URL = env('URL', default=f"{UUID}.loca.lt")
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS', default=[])
CSRF_TRUSTED_ORIGINS += [f"https://{URL}"]
TELEGRAM_LOGS_CHAT_ID = env("TELEGRAM_LOGS_CHAT_ID", default=190444644)
SESAME_TOKEN_NAME = 'secret_token'
API_ID = env('API_ID')
API_HASH = env('API_HASH')
# response = bot.iter_participants(-1001326436004)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'react-modules/',
        'STATS_FILE': os.path.join(BASE_DIR, 'react-modules', 'webpack-stats.json'),
    }
}
# -----> SENTRY
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# from sentry_sdk.integrations.celery import CeleryIntegration
# from sentry_sdk.integrations.redis import RedisIntegration

# sentry_sdk.init(
#     dsn="INPUT ...ingest.sentry.io/ LINK",
#     integrations=[
#         DjangoIntegration(),
#         CeleryIntegration(),
#         RedisIntegration(),
#     ],
#     traces_sample_rate=0.1,

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )
