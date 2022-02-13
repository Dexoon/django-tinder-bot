import json
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden, Http404

from django.conf import settings
from .dispatcher import process_telegram_event
from .models import Chat, User

logger = logging.getLogger(__name__)


def index(request):
    context = {'template': 'chats'}
    if not request.user.is_anonymous:
        user = request.user
        chats = [{'id': c['chat_id'], 'title': c['title']} for c in user.chats.values('chat_id', 'title')]
        react_data = {
            'chats': chats
        }
        context['react_data'] = react_data
    return render(request, "react_template.html", context)


def chat(request, id: str):
    context = {'template': 'tinder'}
    if not request.user.is_anonymous:
        user = request.user
        chat = get_object_or_404(Chat, chat_id=id)
        if not chat in user.chats.all():
            raise Http404()
        user = request.user
        users = chat.users.exclude(user_id=user.user_id).values('user_id', 'username', 'first_name', 'last_name',
                                                                'photos')
        likes = user.crushes.all().values_list('user_id', flat=True)
        followers = user.followers.all().values_list('user_id', flat=True)
        react_data = {
            'users': list(users),
            'likes': list(likes),
            'mutuals': list(set(followers) & set(likes))
        }
        context['react_data'] = react_data
    return render(request, "react_template.html", context)


def like(request, user_id):
    if not request.user.is_anonymous:
        user = request.user
        crush = get_object_or_404(User, user_id=user_id)
        result = user.like(crush)
        return JsonResponse({'ok': True, 'mutual': result})
    raise Http404()


def unlike(request, user_id):
    if not request.user.is_anonymous:
        user = request.user
        crush = get_object_or_404(User, user_id=user_id)
        user.unlike(crush)
        return JsonResponse({'ok': True})
    raise Http404()


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again. 
    # Can be fixed with async celery task execution
    def dispatch(self, request, *args, **kwargs):
        if kwargs['secret'] != settings.SECRET:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if settings.DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)! 
            # Read Procfile for details
            # You can run all of these services via docker-compose.yml
            process_telegram_event.delay(json.loads(request.body))

        # TODO: there is a great trick to send action in webhook response
        # e.g. remove buttons, typing event
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})
