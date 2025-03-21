from django.urls import path
from . import views
# from game_server.views import get_tournament_status
# from .views import tournament_status

urlpatterns = [
    path('', views.index, name='index'),
    # path('tournament-status/', views.get_tournament_status, name='get_tournament_status'),
    #path('api/tournament-status/', views.get_tournament_status, name='get_tournament_status'),
    #path('start-game/', views.start_game, name='start_game'),
]


