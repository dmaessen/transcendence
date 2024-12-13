"""
<<<<<<< HEAD:Transcendence/wsgi.py
WSGI config for transcendence project.
=======
WSGI config for backend project.
>>>>>>> main:backend/backend/wsgi.py

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

<<<<<<< HEAD:Transcendence/wsgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Transcendence.settings')
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
>>>>>>> main:backend/backend/wsgi.py

application = get_wsgi_application()
