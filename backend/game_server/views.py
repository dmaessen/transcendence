import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def index(request):
    return render(request, 'index.html')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tournament_status(request):
    state = cache.get("tournament_state")
    if state:
        state = json.loads(state)
    else:
        state = {
            "tournament_db_id": None,
            "tournament_active": False,
            "players_in": 0,
            "remaining_spots": 4,
            "players": [],
            "bracket": {},
            "current_round": 1,
            "running": False,
            "final_winner": None,
            "matches": [],
            "winners": []
        }  # Default state
    return JsonResponse(state)
