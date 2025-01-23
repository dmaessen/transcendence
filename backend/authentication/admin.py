from django.contrib import admin
from data.models import CustomUser, Match, Tournament  # Import your models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

# admin.site.register(CustomUser)  # Register the User model
admin.site.register(Match)  # Optional, for other models
admin.site.register(Tournament)  # Optional, for other models
