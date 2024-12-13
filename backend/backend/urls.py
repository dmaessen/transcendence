"""
<<<<<<< HEAD:Transcendence/urls.py
URL configuration for transcendence project.
=======
URL configuration for backend project.
>>>>>>> main:backend/backend/urls.py

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
<<<<<<< HEAD:Transcendence/urls.py
from django.urls import path
from . import views
=======
from django.urls import path, include
>>>>>>> main:backend/backend/urls.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('matchmaking/', include('matchmaking.urls'), name='matchmaking'),

]
