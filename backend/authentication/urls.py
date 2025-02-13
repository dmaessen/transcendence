from django.urls import path, include
# from dj_rest_auth import get_refresh_view
# from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, sign_out, home

urlpatterns = [
	path('', home, name='home'),
	path('sign_out', sign_out, name= 'sign_out'),
	path('login/', LoginView.as_view(), name='login'),
	path('register/', RegisterView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh')
]