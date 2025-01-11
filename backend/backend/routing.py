# routing.py
from django.urls import re_path # remove?
from django.urls import path
from game_server.consumers import GameConsumer

websocket_urlpatterns = [
    #re_path(r'ws/game_server/$', GameConsumer.as_asgi()),
    path('ws/game_server/', GameConsumer.as_asgi()),
]