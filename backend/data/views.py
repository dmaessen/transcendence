from data.models import *
from django.http import JsonResponse
from data.services import *
from data.serializers import *
import logging
import json
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

 
from rich import print

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    logger.info(f"Request: {request.user.id}")
    
    profileID = request.GET.get("userID")
    friendshipID = None
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user
        btnType = "Edit profile"
    else:
        user = CustomUser.objects.filter(id = profileID).first()
        friendship = get_frienship(profileID, request.user.id)
        if friendship:
            friendshipID =  friendship.id
            if friendship.status == "approved":
                btnType = "Delete friend"
            elif friendship.status == "pending" and friendship.sender == request.user:
                btnType = "Friend request sent"
            else:
                btnType = "Accept request"
        else:
            btnType = "Add friend"
        
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    matches_played = get_matches_count(user.id)
    matches_won = get_win_cout(user.id)
    matches_lost = matches_played - matches_won
    
    logging.info(f"btn: {btnType}")
    user_data = {
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar.url if user.avatar else None,
        "btnType": btnType,
        "matches_played": matches_played,
        "matches_won": matches_won,
        "matches_lost": matches_lost,
        "user_id": user.id,
        "friendshipID": friendshipID
    }
    logging.info(f"userdata: {user_data}")

    return JsonResponse(user_data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_matches(request):
    logger.info(f"Request {request}")
    
    profileID = request.GET.get("userID")
    
    if profileID == "self":
        user = request.user
    else:
        user = CustomUser.objects.filter(id = profileID).first()
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
    logger.info(f"Request {request}")
    
    profileID = request.GET.get("userID")
    
    if profileID == "self" or request.user.id == int(profileID):
        user = request.user
    else:
        user = CustomUser.objects.filter(id=profileID).first()
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
    logger.info("Changing user data \n")
    
    newUsername = request.POST.get('newUsername')
    newMail = request.POST.get('newMail')
    newAvatar = request.FILES.get('newAvatar')
    

    logger.info(f"newUsername: {newUsername}")
    logger.info(f"newMail: {newMail}")
    
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
        logger.error(f"Error edting user data: {e}")
        return JsonResponse({"error": "Oopsie, something went wrong"}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_friends(request):
    user = request.user
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    friends = get_friends(user.id)
    return JsonResponse(friends, safe=False)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_friend(request):
    user = request.user
    friendID = request.data.get('userID')
    if friendID is None:
        return JsonResponse({"message": "Missing data"}, status=400)
    logging.info(f"user id {user.id} and friendID: {friendID}")
    add_new_friend(user.id, friendID)
    return JsonResponse({"success": True, "message": "Friend request sent"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_friend(request):
    user = request.user
    friendID = request.data.get("userID")
    if friendID is None:
        return JsonResponse({"message": "Missing data"}, status=400)
    logging.info(f"user id {user.id} and friendID: {friendID}")
    remove_friend(user.id, friendID)
    return JsonResponse({"success": True, "message": "Friend removed"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def friends_requests(request):
    user = request.user
    fRequests = get_friendship_requests(user.id)

    return JsonResponse(fRequests, safe=False)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friendship(request):
    friendship_id = request.data.get("friendshipID")
    accept_friend(friendship_id)
    return JsonResponse({"success": True, "message": "friendship created"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_friendship(request):
    friendship_id = request.data.get("friendshipID")
    cancel_friend(friendship_id)
    return JsonResponse({"success": True, "message": "friendship canceled"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_user(request):
    username = request.GET.get("friendUsername")
    try:
        user = CustomUser.objects.get(username=username)
        return JsonResponse({"user_id": user.id})
    except CustomUser.DoesNotExist:
        return JsonResponse({"user_id": None})
