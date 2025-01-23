from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Adjust this import to match your model's location

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Customize list_display without first_name and last_name
    list_display = ('id', 'email', 'username', 'is_active', 'is_staff', 'is_superuser')
    
    # Customize fields if needed
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('location', 'oauth_tokens')}),
        )