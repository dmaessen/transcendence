from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import PlayerQueue, Match

from rest_framework.parsers import JSONParser
from .serializers import PlayerQueueSerializer, MatchSerializer

#@api_view(['GET'])
def index(request):
    return HttpResponse("HI I AM THE BANANA and THIS IS INDEX")

@api_view(['GET'])
def list_players(request):
    players = PlayerQueue.objects.all()

    serializer = PlayerQueueSerializer(players, many=True)
    return JsonResponse(serializer.data, safe=False)



#rest api version, using serializer.
@api_view(['POST'])
def join_queue(request):
    data = JSONParser().parse(request)

    #check if new player exists in queue
    if PlayerQueue.objects.filter(player_id=data.get('player_id')).exists():
        return JsonResponse({"error": "Player is already in the queue."},
            status=400
        )

    serializer = PlayerQueueSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

#without rest api version. json serializer defined in fuction seperately

# @api_view(['POST'])
# def join_queue(request):
#     player_id = request.data['player_id']
#     skill_level = request.data['skill_level']
#     total_wins = request.data['total_wins']

#     #instead of this use REST
#     PlayerQueue.objects.create(
#         player_id=player_id,
#         skill_level=skill_level,
#         total_wins=total_wins,
#     )

#     return Response({'status': 'Player added to queue', 'player_id': player_id})


@api_view(['POST'])
def create_matches(request):
    players = PlayerQueue.objects.order_by('total_wins') #sorts ascending order
    #players = PlayerQueue.objects.all()

    matches = []
    while len(players) > 1:
        player1 = players[0]
        player2 = players[1]
        match = Match.objects.create(player1=player1.player_id, player2=player2.player_id)
        matches.append(match)

        # Remove paired players from the queue
        players = players[2:]

    return JsonResponse({"message": "Matches created.", "matches": [str(m) for m in matches]}, status=201)
