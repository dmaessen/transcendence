from django.contrib import admin
from data.models import User, Match, Tournament  # Import your models

admin.site.register(User)  # Register the User model
admin.site.register(Match)  # Optional, for other models
admin.site.register(Tournament)  # Optional, for other models
