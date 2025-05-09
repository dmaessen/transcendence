from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None  # No token → skip auth

        try:
            validated_token = AccessToken(access_token)
            user_id = validated_token.get("user_id")
            user = User.objects.get(id=user_id)
        except Exception as e:
            raise AuthenticationFailed("Invalid access token")

        return (user, None)