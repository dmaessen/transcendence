from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
# from corsheaders.decorators import cors_allow_all_origins

# @csrf_exempt
# @cors_allow_all_origins

def index(request):
    return render(request, 'game_server/index.html')

def get_tournament_status(request):
    state = cache.get("tournament_state", {"tournament_active": False})
    return JsonResponse(state)
# def start_game(request):
    # if request.method == "POST":
    #     game = Game(mode="singleplayer")  # ex
    #     return JsonResponse({"status": "Game started", "game_id": id(game)})
