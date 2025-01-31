from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from data.models import User, Match
from rest_framework.parsers import JSONParser
from data.serializers import UserSerializer, MatchSerializer
from .game_state import player_queue
from asgiref.sync import sync_to_async



async def create_match(player_id):
    global player_queue
    #player_id = request.user.id
    player_queue.append(player_id)
    # print("player_id= ", player_id)
    # print("len(player_queue)= ", len(player_queue))

    # if not request.user or request.user.is_anonymous:
    #     return JsonResponse({"message": "Authentication required to play a game."}, status=401)
    #print("player_queue= ", player_queue)
    matches = []
    if len(player_queue) <= 1:
        #return JsonResponse({"message": "Match is not created, no enough player"}, status=404)
        return None

    #player1 = User.objects.get(id=player_queue[0])
    player1 = await sync_to_async(User.objects.get)(id=player_queue[0])
    #player2 = User.objects.get(id=player_queue[1])
    player2 = await sync_to_async(User.objects.get)(id=player_queue[1])

    #match = Match.objects.create(player_1=player1, player_2=player2, match_time=timedelta(minutes=2))
    match = await sync_to_async(Match.objects.create)(
        player_1=player1, player_2=player2, match_time=timedelta(minutes=2)
    )
    matches.append(match)
    player_queue.pop(0)
    player_queue.pop(0)

    # serialize for printing and return match information
    #serializer = MatchSerializer(matches, many=True)
    # Serialize the match data
    match_data = await sync_to_async(lambda: MatchSerializer(match).data)()

    return match_data
    #return JsonResponse({"message": "Matches created.", "matches": serializer.data}, status=201)
    #return f"room_for_{player_id}" 