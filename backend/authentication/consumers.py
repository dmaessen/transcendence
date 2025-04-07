from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import logging
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from data.models import *

logger = logging.getLogger(__name__)

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        logger.info(f"user {self.username} with id {self.id} is now connected")
        if user.is_authenticated:
            cache.set(f"user_online_{self.id}", True, timeout=300)  # Set for 5 minutes
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        logger.info(f"user {user.username} is now disconnected")
        if user.is_authenticated:
            cache.delete(f"user_online_{user.id}")
