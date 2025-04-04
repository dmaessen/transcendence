# routing.py
from django.urls import re_path
from django.urls import path
from game_server.consumers import *
from game_server.tournament_consumers import TournamentConsumer

websocket_urlpatterns = [
    #re_path(r'ws/game_server/$', GameConsumer.as_asgi()),
    path('ws/game_server/', GameConsumer.as_asgi()),
    path('ws/tournament/', TournamentConsumer.as_asgi()),
    path('ws/online_users/', UserStatusConsumer.as_asgi())
    # re_path(r'ws/tournament/(?P<tournament_id>\w+)/game/(?P<game_id>\w+)/$', GameConsumer.as_asgi()),
]