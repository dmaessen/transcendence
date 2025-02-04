from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from data.models import User, Match
from data.serializers import UserSerializer, MatchSerializer
from .game_state import player_queue
from types import SimpleNamespace
from asgiref.sync import sync_to_async

"""
the issue was when we have a guest player (during the dev test when i press button for 2 player])

guest players dont need to pass to db because they dont have user accounts
Sothat i can make a class (maybe a matchmaking class) and give it a guestuser??
"""

async def create_match(player_id):
    global player_queue

    if player_id is None:
        # assign negative IDs for guests
        guest_id = -len(player_queue) - 1
        player_queue.append(guest_id)
    else:
        player_queue.append(player_id)

    if len(player_queue) <= 1:
        return "waiting"

    player1 = player_queue.pop(0)
    player2 = player_queue.pop(0)

    # If a player is a guest with negative id, create a fake user object
    def get_user(player):
        if player < 0:
            return SimpleNamespace(id=player, username=f"Guest {abs(player)}")
        return User.objects.get(id=player)

    player1 = await sync_to_async(get_user)(player1)
    player2 = await sync_to_async(get_user)(player2)

    match = await sync_to_async(Match.objects.create)(
        player_1=player1.id, player_2=player2.id, match_time=timedelta(minutes=2)
    )

    return {"id": match.id, "player_1": player1.id, "player_2": player2.id}


# async def create_match(player_id):
#     global player_queue

#     if player_id is None:
#         guest_id = -len(player_queue) - 1  # Assign negative IDs for guests
#         player_queue.append(guest_id)
#     else:
#         player_queue.append(player_id)
#     #player_queue.append(player_id)
#     # print("player_id= ", player_id)
#     # print("len(player_queue)= ", len(player_queue))

#     # if not request.user or request.user.is_anonymous:
#     #     return JsonResponse({"message": "Authentication required to play a game."}, status=401)
#     #print("player_queue= ", player_queue)
#     matches = []
#     if len(player_queue) <= 1:
#         return "waiting"  # Indicate that we're waiting for another player
#     print("PLAYER_1 ", player_queue[0])
#     print("PLAYER_2 ", player_queue[1])

#         # If a player is a guest (negative ID), create a fake user object
#     def get_user(player):
#         if player < 0:
#             return SimpleNamespace(id=player, username=f"Guest {abs(player)}")
#         return User.objects.get(id=player)

#     #player1 = User.objects.get(id=player_queue[0])
#     player1 = await sync_to_async(User.objects.get)(id=player_queue[0])
#     #player2 = User.objects.get(id=player_queue[1])
#     player2 = await sync_to_async(User.objects.get)(id=player_queue[1])

#     #match = Match.objects.create(player_1=player1, player_2=player2, match_time=timedelta(minutes=2))
#     match = await sync_to_async(Match.objects.create)(
#         player_1=player1, player_2=player2, match_time=timedelta(minutes=2)
#     )
#     matches.append(match)
#     player_queue.pop(0)
#     player_queue.pop(0)

#     # serialize for printing and return match information
#     #serializer = MatchSerializer(matches, many=True)
#     # Serialize the match data
#     match_data = await sync_to_async(lambda: MatchSerializer(match).data)()

#     return match_data