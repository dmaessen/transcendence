from django.shortcuts import render
from django.http import JsonResponse
from .game_logic import Game  # Replace 'GameLogic' with the class/function name.
#from .game_server import GameServer  # Replace 'GameServer' with the class/function name.

def index(request):
    return render(request, 'game_server/index.html')

# def start_game(request):
    # if request.method == "POST":
    #     game = Game(mode="singleplayer")  # ex
    #     return JsonResponse({"status": "Game started", "game_id": id(game)})
