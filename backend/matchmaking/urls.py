from django.urls import path

from . import views
from .views import join_queue

urlpatterns = [
    path("", views.index, name="index"),
    path('api/join/', views.join_queue, name='join_queue'),
    path('api/players/', views.list_players, name='list_players'),
    path('api/create_match/', views.create_matches, name='create_match'),
    path('api/matches/', views.list_matches, name='matches'),

]