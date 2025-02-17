from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
# from corsheaders.decorators import cors_allow_all_origins

# @csrf_exempt
# @cors_allow_all_origins

def index(request):
    return render(request, 'index.html')

def get_tournament_status(request):
    state = cache.get("tournament_state", {"tournament_active": False, "players_in": 0, "remaining_spots": 4})  # Default state
    return JsonResponse(state)

# def tournament_status(request):
#     return JsonResponse({"status": "Tournament endpoint working!"})


# def get_tournament_status(request):
#     state = cache.get("tournament_state", {"tournament_active": True})
#     return JsonResponse(state)