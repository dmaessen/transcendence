"""
<<<<<<< HEAD:Transcendence/asgi.py
ASGI config for transcendence project.
=======
ASGI config for backend project.
>>>>>>> main:backend/backend/asgi.py

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD:Transcendence/asgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Transcnedence.settings')
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
>>>>>>> main:backend/backend/asgi.py

application = get_asgi_application()
