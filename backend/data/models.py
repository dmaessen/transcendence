from django.db import models
# from cryptography.fields import encrypt  # Assuming this is a custom field for encryption
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import get_language
from django.conf import settings

class CustomUserManager(BaseUserManager):

    def create_user(self, name, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Unique email for login
    name = models.CharField(max_length=30)
    username = models.CharField(unique=True, max_length=30) # Unique as well
    two_factor_enabled = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', default='default.png')
    oauth_tokens = models.JSONField(null=True, blank=True)
    tournaments = models.ManyToManyField('Tournament', related_name='players', blank=True)
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    preferred_language = models.CharField(
        max_length=10, 
        choices=settings.LANGUAGES, 
        default=settings.LANGUAGE_CODE
    )

    # User manager
    objects = CustomUserManager()

    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']  # Name is required when creating a superuser
   
    def _str_(self):
        return self.name

class Friendship(models.Model):
    sender = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendship_creator_set')
    receiver = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendship_receiver_set')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('approved', 'Approved')))

    class Meta:
        unique_together = ('sender', 'receiver')

class Match(models.Model):
    player_1 = models.ForeignKey(CustomUser, related_name="player_1_matches", on_delete=models.SET_NULL, null=True)
    player_2 = models.ForeignKey(CustomUser, related_name="player_2_matches", on_delete=models.SET_NULL, null=True)
    player_1_points = models.IntegerField(default=0)
    player_2_points = models.IntegerField(default=0)
    match_start = models.DateTimeField(null=True, blank=True)
    match_time = models.DurationField()
    winner = models.ForeignKey(CustomUser, related_name="match_winner", on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey('Tournament', related_name="matches", on_delete=models.SET_NULL, null=True, blank=True)  # Tournament for match, null if not part of any

    def __str__(self):
        return f"Match_{self.player_1}.vs.{self.player_2} Winner: {self.winner}"


class Tournament(models.Model):
    max_players = models.IntegerField(default=8)  # 4 or 8 players
    
    first_place = models.ForeignKey(CustomUser, related_name="first_place", on_delete=models.SET_NULL, null=True, blank=True)
    second_place = models.ForeignKey(CustomUser, related_name="second_place", on_delete=models.SET_NULL, null=True, blank=True)
    third_place = models.ForeignKey(CustomUser, related_name="third_place", on_delete=models.SET_NULL, null=True, blank=True)
    fourth_place = models. ForeignKey(CustomUser, related_name="fourth_place", on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Tournament {self.id}: (Start: {self.start_date})"
