"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from data.views import *
from django.conf import settings
from django.conf.urls.static import static
from game_server.views import get_tournament_status
from django.conf.urls.i18n import i18n_patterns, set_language
from .views import index

urlpatterns = [
    path('', index),
    #path('i18n/', include('django.conf.urls.i18n')),
    # path('i18n/', set_language, name='set_language'),
    path('i18n/setlang/', set_language, name='set_language'),
    path('matchmaking/', include('matchmaking.urls')),
    path('game_server/', include('game_server.urls')),
	path('api/authentication/', include('authentication.urls')),
    path('data/', include('data.urls')),
    path("accounts/", include("allauth.urls")),
    path("accounts/2fa", include("allauth_2fa.urls")),
    #path('api/', include('game_server.urls')),
    path('tournament-status/', get_tournament_status, name='tournament-status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
