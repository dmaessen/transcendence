from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from data.models import CustomUser, Match
from rest_framework.parsers import JSONParser
from data.serializers import UserSerializer, MatchSerializer
from .game_state import player_queue

import logging

#@api_view(['GET'])
def index(request):
    return HttpResponse("HI I AM THE BANANA and THIS IS INDEX")

@api_view(['GET'])
def list_players(request):
   return JsonResponse({"queue": player_queue}, status=200)

@api_view(['POST'])
def create_a_match(request):
    global player_queue
    player_id = request.user.id
    player_queue.append(player_id)

    if not request.user or request.user.is_anonymous:
        return JsonResponse({"message": "Authentication required to play a game."}, status=401)
    matches = []
    if len(player_queue) <= 1:
        return JsonResponse({"message": "Match is not created, no enough player"}, status=404)

    elif len(player_queue) > 1:
        player1 = User.objects.get(id=player_queue[0])
        player2 = User.objects.get(id=player_queue[1])
        match = Match.objects.create(player_1=player1, player_2=player2, match_time=timedelta(minutes=2))
        matches.append(match)
        player_queue.pop(0)
        player_queue.pop(0)

    serializer = MatchSerializer(matches, many=True)
    return JsonResponse({"message": "Matches created.", "matches": serializer.data}, status=201)

@api_view(['POST'])
def create_matches(request):
    global player_queue
    player_id = request.user.id
    
    player_queue.append(player_id)

    if len(player_queue) <= 1:
        return JsonResponse({"message": "Match is not created, no enough player"}, status=404)

    matches = []

    print("player0 ID ", player_queue[0])
    print("player1 ID ", player_queue[1])
    print("player_queue= ", player_queue)

    while len(player_queue) > 1:
        player1 = User.objects.get(id=player_queue[0])
        player2 = get_object_or_404(User, id=player_queue[1])
        player2 = User.objects.get(id=player_queue[1])
        match = Match.objects.create(player_1=player1, player_2=player2, match_time=timedelta(minutes=3))
        matches.append(match)
        player_queue.pop(0)
        player_queue.pop(0)

    serializer = MatchSerializer(matches, many=True)
    return JsonResponse({"message": "Matches created.", "matches": serializer.data}, status=201)

@api_view(['GET'])
def list_matches(request):
    """
    Displays all created matches.
    """
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)

    return Response(serializer.data)
