from django.urls import path
from .views import *

urlpatterns = [
    path("api/userData/", get_user_data, name="get_user_data"),
    path("api/userMatches/", get_user_matches, name="get_user_matches"),
    path("api/userTournaments/", get_user_tournaments, name="get_user_tournaments"),
    path("api/editProfile/", edit_user_data, name="edit_user_data"),
]


