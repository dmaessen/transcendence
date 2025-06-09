from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import logging
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from data.models import *
from data.services import *
import jwt
import json
from authentication.views import *
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            cookies = self.scope.get("headers", [])
            token = None
            for header in cookies:
                if header[0].decode("utf-8") == "cookie":
                    cookie_header = header[1].decode("utf-8")
                    cookies_dict = {k.strip(): v.strip() for k, v in (cookie.split("=") for cookie in cookie_header.split(";"))}
                    token = cookies_dict.get("access_token")
                    break
            if token:
                # Validate the JWT token
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                
                # Fetch the user from the database based on the user_id
                user = await sync_to_async(CustomUser.objects.get)(id=user_id)
                logger.info(f"[AUTH_CONSUMER]username: {user.username}")
                self.scope["user"] = user  # Assign the user to the scope 
            else:
                logger.warning("[AUTH_CONSUMER]No token provided.")
                await self.close()  # Close if no token is provided
        except Exception as ex:
            logger.error(f"[AUTH_CONSUMER]WebSocket connect error: {ex}")
            await self.close()
            
        # If the user is authenticated, mark them as online
        if self.scope["user"].is_authenticated:
            cache.set(f"user_online_{user.id}", True, timeout=None)
            logger.info(f"[AUTH_CONSUMER]user {user.username} is cached")

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get("type") == "ping":
            user = self.scope["user"]
            if user.is_authenticated:
                cache.set(f"user_online_{user.id}", True, timeout=3000)
        await self.send(text_data=json.dumps({"type": "pong"}))

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            logger.info(f"[AUTH_CONSUMER]user {user.username} is now disconnected")
            cache.delete(f"user_online_{user.id}")
            logger.info(f"[AUTH_CONSUMER]user {user.username} is decached")
            