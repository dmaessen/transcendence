from data.models import *
from django.http import JsonResponse
from data.services import *
from data.serializers import *
import logging
import json
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
 
from rich import print

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    logging.info(f"Request: {request.user.id}")

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    user = request.user
    
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    user_data = {
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar.url if user.avatar else None,
    }

    return JsonResponse(user_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_matches(request):
    logging.info(f"Request {request}")
    
    user = request.user
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    matches = get_user_3_matches(user.id)
    match_data = {
        "matches": list(MatchSummarySerializer(matches, many=True, context={"user": user}).data),
    }

    return JsonResponse(match_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_tournaments(request):
    logging.info(f"Request {request}")
    
    user = request.user
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    tournaments = get_user_3_tournaments(user.id)
    tournaments_data = {
        "tournaments": list(TournamentSummarySerializer(tournaments, many=True).data),
    }

    return JsonResponse(tournaments_data, safe=False)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_user_data(request):
    logging.info("Changing user data \n")
    
    newUsername = request.POST.get('newUsername')
    newMail = request.POST.get('newMail')
    newAvatar = request.FILES.get('newAvatar')
    
    logging.info(f"newUsername: {newUsername}")
    logging.info(f"newMail: {newMail}")
    
    user = request.user
    
    try:
        # Check if username or email already exists
        if newUsername and CustomUser.objects.exclude(id=user.id).filter(username=newUsername).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)

        if newMail and CustomUser.objects.exclude(id=user.id).filter(email=newMail).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        # Update only if values are provided
        if newUsername:
            user.username = newUsername
        if newMail:
            user.email = newMail
        if newAvatar:
            user.avatar = newAvatar

        user.save()
        
        updated_user_data = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar.url if user.avatar else None,
        }
                
        return JsonResponse({"message": "Successfully edited", "user_data": updated_user_data}, status=200)
    
    except Exception as e:
        logging.error(f"Error edting user data: {e}")
        return JsonResponse({"error": "Oopsie, something went wrong"}, status=500)




