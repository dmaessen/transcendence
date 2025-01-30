from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/players/', views.list_players, name='list_players'),
    path('api/create_a_match/', views.create_a_match, name='create_a_match'),
    path('api/create_matches/', views.create_matches, name='create_matches'),
    path('api/matches/', views.list_matches, name='matches'),
]