# from django.http import JsonResponse
# from data.services import *
# from data.serializers import *
# import logging

# logger = logging.getLogger(__name__)

# def my_view(request):
#     logger.debug("This is a debug message from views.py")
#     logger.info("This is an info message from views.py")
#     logger.warning("This is a warning message from views.py")

# # @login_required
# def get_user_data(request):
#     logging.info(f"Request {request}")
    
#     testUser = CustomUser.objects.filter(id=4).first()
#     if not testUser:
#         return JsonResponse({"error": "User not found"}, status=404)

#     matches = get_user_3_matches(testUser.id)
#     tournaments = get_user_3_tournaments(testUser.id)
#     user_data = {
#         "username": testUser.username,
#         "email": testUser.email,
#         "avatar": testUser.avatar.url,
#         # "matches": MatchSummarySerializer(matches, many=True, context={"user": testUser}).data,
#         # "tournaments": TournamentSummarySerializer(tournaments, many=True).data,
#         "matches": list(MatchSummarySerializer(matches, many=True, context={"user": testUser}).data),
#         "tournaments": list(TournamentSummarySerializer(tournaments, many=True).data),

#     }
#     logging.info(f"Response JSON: {user_data}")
#     return JsonResponse(user_data)

from data.models import *
from django.http import JsonResponse
from data.services import *
from data.serializers import *
import logging
import json
from django.contrib.auth.decorators import login_required
 
from rich import print

logger = logging.getLogger(__name__)

#@login_required
def get_user_data(request):
    logging.info(f"Request:\n {request.user.id}")

    testUser = request.user.id
    
    if not testUser:
        return JsonResponse({"error": "User not found"}, status=404)

    # matches = get_user_3_matches(testUser.id)
    # tournaments = get_user_3_tournaments(testUser.id)

    user_data = {
        "username": testUser.username,
        "email": testUser.email,
        "avatar": testUser.avatar.url if testUser.avatar else None,
        # "matches": list(MatchSummarySerializer(matches, many=True, context={"user": testUser}).data),
        # "tournaments": list(TournamentSummarySerializer(tournaments, many=True).data),
    }

    # Log as a properly formatted and colorful JSON string
    logging.info("Response JSON:\n" + json.dumps(user_data, indent=2, default=str))

    # Print it in the terminal with colors - that was the idea at least 
    print("[bold cyan]Response JSON:[/bold cyan]")
    print(json.dumps(user_data, indent=2, default=str))

    return JsonResponse(user_data, safe=False)

def get_user_matches(request):
    logging.info(f"Request {request}")
    
    testUser = CustomUser.objects.filter(id=4).first()
    if not testUser:
        return JsonResponse({"error": "User not found"}, status=404)

    matches = get_user_3_matches(testUser.id)
    match_data = {
        "matches": list(MatchSummarySerializer(matches, many=True, context={"user": testUser}).data),
    }
    
    # Log as a properly formatted and colorful JSON string
    logging.info("Response JSON:\n" + json.dumps(match_data, indent=2, default=str))

    # Print it in the terminal with colors - that was the idea at least 
    print("[bold cyan]Response JSON:[/bold cyan]")
    print(json.dumps(match_data, indent=2, default=str))
    
    return JsonResponse(match_data, safe=False)

def get_user_tournaments(request):
    logging.info(f"Request {request}")
    
    testUser = CustomUser.objects.filter(id=4).first()
    if not testUser:
        return JsonResponse({"error": "User not found"}, status=404)
    
    tournaments = get_user_3_tournaments(testUser.id)
    tournaments_data = {
        "tournaments": list(TournamentSummarySerializer(tournaments, many=True).data),
    }
    # Log as a properly formatted and colorful JSON string
    logging.info("Response JSON:\n" + json.dumps(tournaments_data, indent=2, default=str))

    # Print it in the terminal with colors - that was the idea at least 
    print("[bold cyan]Response JSON:[/bold cyan]")
    print(json.dumps(tournaments_data, indent=2, default=str))
    
    return JsonResponse(tournaments_data, safe=False)




