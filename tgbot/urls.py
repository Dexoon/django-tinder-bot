from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    # TODO: make webhook more secure
    path('', views.index, name="index"),
    path('chat/<str:id>/', views.chat, name="chat"),
    path('webhook/telegram/<str:secret>/', csrf_exempt(views.TelegramBotWebhookView.as_view())),
    path('like/<int:user_id>/', views.like, name="like"),
    path('unlike/<int:user_id>/', views.unlike, name="unlike"),

]
