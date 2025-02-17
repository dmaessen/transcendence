"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from game_server.consumers import GameConsumer
from game_server.tournament_consumers import TournamentConsumer
from backend.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

#application = get_asgi_application()

application = ProtocolTypeRouter({
    #"http": django_asgi_app,
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
        # URLRouter({
        #     "game_server/": GameConsumer.as_asgi(),
        #     path("ws/game_server/", GameConsumer.as_asgi()),
        # })
    ),
})



# from django.core.asgi import get_asgi_application
# from django.urls import re_path

# # Initialize Django ASGI application early to ensure the AppRegistry
# # is populated before importing code that may import ORM models.
# django_asgi_app = get_asgi_application()

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter([
#                 re_path(r"^front(end)/$", consumers.AsyncChatConsumer.as_asgi()),
#             ])
#         )
#     ),
# })

#Channels introduces the idea of a channel layer, a low-level abstraction around a set of transports
# that allow you to send information between different processes.
# Each application instance has a unique channel name, and can join groups, allowing both point-to-point and broadcast messaging.



# from django.core.asgi import get_asgi_application
# from django.urls import re_path

# # Initialize Django ASGI application early to ensure the AppRegistry
# # is populated before importing code that may import ORM models.
# django_asgi_app = get_asgi_application()

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter([
#                 re_path(r"^front(end)/$", consumers.AsyncChatConsumer.as_asgi()),
#             ])
#         )
#     ),
# })