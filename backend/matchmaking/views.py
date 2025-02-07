from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from data.models import CustomUser, Match
from rest_framework.parsers import JSONParser
from data.serializers import UserSerializer, MatchSerializer
from . import game_state

#@api_view(['GET'])
def index(request):
    return HttpResponse("HI I AM THE BANANA and THIS IS INDEX")

@api_view(['GET'])
def list_players(request):
    return player_queue

#rest api version, using serializer.
# @api_view(['POST'])
# def join_players_queue(request):
#     data = JSONParser().parse(request)

#     #check if new player exists in queue
#     if User.objects.filter(name=data.get('name')).exists():
#         return JsonResponse({"error": "Player name is already used."},
#             status=400
#         )

#     serializer = UserSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return JsonResponse(serializer.data, status=201)
#     return JsonResponse(serializer.errors, status=400)

#without rest api version. json serializer defined in fuction seperately

# @api_view(['POST'])
# def join_players_queue(request):
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

#for a single game?
@api_view(['POST'])
def create_a_match(request):

    player_id = request.user.id
    player_queue.append(player_id)

    matches = []
    if len(player_queue) <= 1:
        return JsonResponse({"message": "Match is not created, no enough player"}, status=404)

    elif len(player_queue) > 1:
        player1 = players[0]
        player2 = players[1]
        match = Match.objects.create(player_1=player1, player_2=player2, match_time=timezone.now())
        matches.append(match)

        # # remove paired players from the queue ?? not sure? maybe add is_active to playerqueue model??
        #players = players[2:]
        #LAURAAA
            #change flag for is_in_queue for player

        # player1.is_active = False
        # player2.is_active = False
        # player1.save()
        # player2.save()

        #change players in function scope
        #players = User.objects.filter(is_active=True).order_by('total_wins')

    # serialize for printing and return match information
    serializer = MatchSerializer(matches, many=True)
    return JsonResponse({"message": "Matches created.", "matches": serializer.data}, status=201)
    #return JsonResponse({"message": "Match is created.", "matches": [str(m) for m in matches]}, status=201)

#for tournament?
@api_view(['POST'])
def create_matches(request):
    player_id = request.user.id
    player_queue.append(player_id)    #     if User.objects.filter(name=data.get('name')).exists():

    #players = PlayerQueue.objects.all()
    if len(player_queue) <= 1:
        return JsonResponse({"message": "Match is not created, no enough player"}, status=404)

    matches = []
    while len(player_queue) > 1:
        player1 = players[0]
        player2 = players[1]
        match = Match.objects.create(player_1=player1, player_2=player2, match_time=timezone.now())
        matches.append(match)

        # # remove paired players from the queue ?? not sure? maybe add is_active to playerqueue model??
        player_queue = player_queue[2:]

    # serialize for printing and return match information
    serializer = MatchSerializer(matches, many=True)
    return JsonResponse({"message": "Matches created.", "matches": serializer.data}, status=201)
    #return JsonResponse({"message": "Match is created.", "matches": [str(m) for m in matches]}, status=201)

@api_view(['GET'])
def list_matches(request):
    """
    Displays all created matches.
    """
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)

    return Response(serializer.data) #same as below
    #return JsonResponse(serializer.data, safe=False)

# @api_view(['GET'])
# def list_tournaments(request):
#     tournaments = Tournament.objects.all()
#     serializer = TournamentSerializer(tournaments, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def create_tournament(request):
    # data = request.data
    # if Tournament.objects.all() == 1
    #     return Response(
    #         {"error": "New tournament can not be started, there is another tournament is already started."},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )
    # if 'number_of_players' not in data or data['number_of_players'] not in [4, 8]:
    #     return Response(
    #         {"error": "Invalid number of players. Only 4 or 8 players are allowed."},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    # data['start_date'] = timezone.now()
    # serializer = TournamentSerializer(data=data)

    # if serializer.is_valid():
    #     tournament = serializer.save()
    #     return Response(
    #         {"message": "Tournament created successfully.", "tournament": serializer.data},
    #         status=status.HTTP_201_CREATED,
    #     )
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#WITHOUT SERIALIZER
#     data = request.data
#     name = data.get('name')
#     max_players = data.get('max_players', 8)  # Default to 8 players

#     if max_players not in [4, 8]:
#         return JsonResponse({"error": "Max players must be 4 or 8."}, status=400)

#     tournament = Tournament.objects.create(name=name, max_players=max_players)
#     return JsonResponse({"message": f"Tournament '{tournament.name}' created."}, status=201)


# @api_view(['POST'])
# def join_tournament(request, tournament_id):
    # tournament = get_object_or_404(Tournament, id=tournament_id)
    # player_id = request.data.get("player_id")

    # if not player_id:
    #     return Response({"error": "Player ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # player = get_object_or_404(User, id=player_id)

    # if tournament.players.count() >= tournament.number_of_players:
    #     return Response(
    #         {"error": "Tournament is already full."},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    # tournament.players.add(player)
    # tournament.save()

    # serializer = TournamentSerializer(tournament)
    # return Response(
    #     {"message": f"Player {player.name} added to tournament.", "tournament": serializer.data},
    #     status=status.HTTP_200_OK,
    # )

#BEFORE SERIALIZER
#     user_id = request.data.get('user_id')
#     user = User.objects.get(id=user_id)
#     tournament = Tournament.objects.get(id=tournament_id)

#     try:
#         tournament.add_player(user)
#         return JsonResponse({"message": f"User {user.name} joined tournament {tournament.name}."}, status=201)
#     except ValueError as e:
#         return JsonResponse({"error": str(e)}, status=400)


# @api_view(['POST'])
# def confirm_ready(request, tournament_id):
#     user_id = request.data.get('user_id')
#     user = User.objects.get(id=user_id)
#     tournament = Tournament.objects.get(id=tournament_id)

#     try:
#         tournament.confirm_ready(user)
#         return JsonResponse({"message": f"User {user.name} is ready for tournament {tournament.name}."}, status=200)
#     except ValueError as e:
#         return JsonResponse({"error": str(e)}, status=400)


# @api_view(['POST'])
# def start_tournament(request, tournament_id):
#     tournament = Tournament.objects.get(id=tournament_id)

#     try:
#         tournament.start_tournament()
#         return JsonResponse({"message": f"Tournament '{tournament.name}' has started."}, status=200)
#     except ValueError as e:
#         return JsonResponse({"error": str(e)}, status=400)

# from django.utils.timezone import now

# @api_view(['POST'])
# def cancel_tournament(request, tournament_id):
#     tournament = Tournament.objects.get(id=tournament_id)
#     if tournament.status != 'open':
#         return JsonResponse({"error": "Cannot cancel a tournament that has already started."}, status=400)
    
#     tournament.status = 'cancelled'
#     tournament.end_date = now()
#     tournament.save()
#     return JsonResponse({"message": f"Tournament '{tournament.name}' has been cancelled."}, status=200)

# timer for auto-cancel, celery, works on background