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
from dj_rest_auth.registration.views import SocialAccountListView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('matchmaking/', include('matchmaking.urls')),
    path('game_server/', include('game_server.urls')),
	path('api/authentication/', include('authentication.urls')),
    path('data/', include('data.urls')),
    path("accounts/", include("allauth.urls")),
    path("accounts/2fa", include("allauth_2fa.urls")),
    path('api/auth/', include('dj_rest_auth.urls')),  # login, logout, etc.
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # signup
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    #path('api/', include('game_server.urls')),
    # path("get_user_data/", get_user_data, name="get_user_data"),
    # path("get_user_matches/", get_user_matches, name="get_user_matches"),
    # path("get_user_tournaments/", get_user_tournaments, name="get_user_tournaments"),
    path('tournament-status/', get_tournament_status, name='tournament-status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
