from django.urls import path
from .views import *

urlpatterns = [
    path("api/userData/", get_user_data, name="get_user_data"),
    path("api/userMatches/", get_user_matches, name="get_user_matches"),
    path("api/userTournaments/", get_user_tournaments, name="get_user_tournaments"),
    path("api/editProfile/", edit_user_data, name="edit_user_data"),
    path("api/searchUser/", search_user, name="search_user"),
    path("api/addFriend/", add_friend, name="add_friend"),
    path("api/deleteFriend/", delete_friend, name="delete_friend"),
    path("api/friendsRequests/", friends_requests, name="friends_requests"),
    path("api/acceptFriendship/", accept_friendship, name="accept_friendship"),
    path("api/cancelFriendship/", cancel_friendship, name="cancel_friendship"),
    path("api/getFriends/", get_user_friends, name="get_user_friends")
]


