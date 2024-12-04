from django.shortcuts import render

from django.http import HttpResponse

#@api_view(['GET'])
def index(request):
    return HttpResponse("HI I AM THE BANANA and THIS IS INDEX")

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import PlayerQueue, Match, MatchResult

@api_view(['POST'])
def join_queue(request):
    player_id = request.data['player_id']
    skill_level = request.data['skill_level']
    total_wins = request.data['total_wins']

    PlayerQueue.objects.create(
        player_id=player_id,
        skill_level=skill_level,
        total_wins=total_wins,
    )

    return Response({'status': 'Player added to queue', 'player_id': player_id})

@api_view(['POST'])
def record_match_result(request):
    match_id = request.data['match_id']
    winner = request.data['winner']
    loser = request.data['loser']

    match = Match.objects.get(id=match_id)
    MatchResult.objects.create(match=match, winner=winner, loser=loser)

    match.completed_at = timezone.now()
    match.winner = winner
    match.save()

    return Response({'status': 'Match result recorded'})
