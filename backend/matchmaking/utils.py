from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from data.models import User, Match
from data.serializers import UserSerializer, MatchSerializer
from .game_state import player_queue
from types import SimpleNamespace
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model


"""
the issue was when we have a guest player (during the dev test when i press button for 2 player])

guest players dont need to pass to db because they dont have user accounts
Sothat i can make a class (maybe a matchmaking class) and give it a guestuser??
"""

from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

async def create_match(player_id):
    global player_queue
    User = get_user_model()

    player_queue.append(player_id)

    if len(player_queue) <= 1:
        return "waiting"

    player1_id = player_queue.pop(0)
    player2_id = player_queue.pop(0)

    # Separate get_user function
    async def resolve_user(player_id):
        try:
            return await sync_to_async(User.objects.get)(id=player_id)
        except User.DoesNotExist:
            return await sync_to_async(User.objects.create)(
                email=f"guest_{player_id}@temp.com", 
                name=f"Guest {player_id}"
            )

    player1 = await resolve_user(player1_id)
    player2 = await resolve_user(player2_id)

    match = await sync_to_async(Match.objects.create)(
        player_1=player1, 
        player_2=player2, 
        match_time=timedelta(minutes=2)
    )

    return {
        "id": match.id, 
        "player_1": player1.id, 
        "player_2": player2.id
    }
