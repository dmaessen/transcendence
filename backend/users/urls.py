from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='join_queue'),
    path('register', views.register, name='list_players'),
    path('logout', views.logout, name='logout'),
]