# routing.py
from django.urls import re_path
from django.urls import path
from game_server.consumers import *
from game_server.tournament_consumers import TournamentConsumer
from authentication.consumers import UserStatusConsumer

websocket_urlpatterns = [
    path('ws/game_server/', GameConsumer.as_asgi()),
    path('ws/tournament/', TournamentConsumer.as_asgi()),
    path('ws/online_users/', UserStatusConsumer.as_asgi())
]