from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache

def index(request):
    return render(request, 'game_server/index.html')

# def start_game(request):
    # if request.method == "POST":
    #     game = Game(mode="singleplayer")  # ex
    #     return JsonResponse({"status": "Game started", "game_id": id(game)})

def get_tournament_status(request):
    """Returns the tournament state for new players who just joined."""
    state = cache.get("tournament_state", {"tournament_active": False})
    return JsonResponse(state)