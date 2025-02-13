from django.http import JsonResponse
from data.services import *
from data.serializers import *
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug("This is a debug message from views.py")
    logger.info("This is an info message from views.py")
    logger.warning("This is a warning message from views.py")

# @login_required
def get_user_data(request):
    logging.info(f"Request {request}")
    
    testUser = CustomUser.objects.filter(id=4).first()
    if not testUser:
        return JsonResponse({"error": "User not found"}, status=404)

    matches = get_user_3_matches(testUser.id)
    tournaments = get_user_3_tournaments(testUser.id)
    user_data = {
        "username": testUser.username,
        "email": testUser.email,
        "avatar": testUser.avatar.url,
        "matches": MatchSummarySerializer(matches, many=True, context={"user": testUser}).data,
        "tournaments": TournamentSummarySerializer(tournaments, many=True).data,
    }
    logging.info(f"Response JSON: {user_data}")
    return JsonResponse(user_data)
