from django.urls import path
from . import views
from game_server import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('start-game/', views.start_game, name='start_game'),
    path('api/tournament-status/', views.get_tournament_status, name='get_tournament_status'),
]
