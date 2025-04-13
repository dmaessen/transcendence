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
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve the token from the query string
        query_params = parse_qs(self.scope["query_string"].decode("utf-8"))
        token = query_params.get("token", [None])[0]
        logger.info(f"querry: {query_params}\ntoken: {token}")
        if token:
            # Validate the JWT token
            access_token = AccessToken(token)
            logger.info(f"----access token: {access_token}\n\n")
            user_id = access_token["user_id"]
            logger.info(f"----userid: {user_id}\n\n")

            # Fetch the user from the database based on the user_id
            user = await sync_to_async(CustomUser.objects.get)(id=user_id)
            logger.info(f"userna: {user.username}")
            self.scope["user"] = user  # Assign the user to the scope
            
            logger.info(f"Authenticated user {user.username} connected via WebSocket.")
        else:
            logger.warning("No token provided.")
            await self.close()  # Close if no token is provided

        # If the user is authenticated, mark them as online
        if self.scope["user"].is_authenticated:
            cache.set(f"user_online_{self.scope['user'].id}", True, timeout=3000)
            logger.info(f"user {user.username} is cached\n\n")

        await self.accept()
        logger.info("WebSocket is on bebe!")

    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f"Gottcha: {text_data}")
        await self.send(text_data="pong")

    async def disconnect(self, close_code):
        user = self.scope["user"]
        logger.info(f"user {user.username} is now disconnected")
        if user.is_authenticated:
            cache.delete(f"user_online_{user.id}")
            logger.info(f"user {user.username} is decached\n\n")
        # await self.send(text_data=json.dumps({"type": "close", "message": "Doei doei!"}))
        # await self.close(code=1000)
