from django.db import models
# from cryptography.fields import encrypt  # Assuming this is a custom field for encryption
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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

#TODO encrypt name, email, location, avatar
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Unique email for login
    name = models.CharField(max_length=30)  # Non-unique name field
    username = models.CharField(unique=True, max_length=30) # Unique as well
    avatar = models.ImageField(upload_to='avatars/', default='default.png')
    location = models.CharField(max_length=30, blank=True, null=True)
    oauth_tokens = models.JSONField(null=True, blank=True)
    tournaments = models.ManyToManyField('Tournament', related_name='players', blank=True)
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # User manager
    objects = CustomUserManager()

    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Name is required when creating a superuser
   
    def _str_(self):
        return self.name

class Friendship(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendship_creator_set')
    friend = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendship_receiver_set')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('approved', 'Approved')))

    class Meta:
        unique_together = ('user', 'friend')

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
        return f"Match_{self.player_1}.vs.{self.player_2}"


class Tournament(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open for Registration'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    max_players = models.IntegerField(default=8)  # 4 or 8 players
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    confirmed_ready = models.ManyToManyField(CustomUser, related_name="ready_players", blank=True)
    
    first_place = models.ForeignKey(CustomUser, related_name="first_place", on_delete=models.SET_NULL, null=True, blank=True)
    second_place = models.ForeignKey(CustomUser, related_name="second_place", on_delete=models.SET_NULL, null=True, blank=True)
    third_place = models.ForeignKey(CustomUser, related_name="third_place", on_delete=models.SET_NULL, null=True, blank=True)
    fourth_place = models. ForeignKey(CustomUser, related_name="fourth_place", on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Tournament {self.id}: {self.status} (Start: {self.start_date})"

    #ADDITIONS FROM GUL:???

# Get all tournaments a player is in:
# player = User.objects.get(id=x)
# tournaments = player.tournaments.all()  # All tournaments the player is part of

# Get all players in a specific tournament:
# tournament = Tournament.objects.get(id=x)
# players = tournament.players.all()  # All players in this tournament

# Get all matches in a specific tournament:
# tournament = Tournament.objects.get(id=x)
# matches = tournament.matches.all()  # All matches in this tournament



# # ASK LAURA
# class Tournament(models.Model):
#     STATUS_CHOICES = [
#         ('open', 'Open for Registration'),
#         ('ongoing', 'Ongoing'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ]

#     max_players = models.IntegerField(default=8)  # 4 or 8 players
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

#     players = models.ManyToManyField(User, related_name="tournaments", blank=True)
#     confirmed_ready = models.ManyToManyField(User, related_name="ready_players", blank=True)

#     def add_player(self, player):
#         """
#         adds a player to the tournament if it's open and not full.
#         """
#         if self.status != 'open':
#             raise ValueError("Cannot join a tournament that is not open.")
#         if self.players.count() >= self.max_players:
#             raise ValueError("Tournament is already full.")
#         self.players.add(player)
#         self.number_of_players += 1
#         self.save()

#     def confirm_ready(self, player):
#         """
#         player confirms they're ready to play.
#         """
#         if player not in self.players.all():
#             raise ValueError("Player is not part of this tournament.")
#         self.confirmed_ready.add(player)
#         self.save()

#     def start_tournament(self):
#         """
#         atarts the tournament if enough players are confirmed ready.
#         """
#         if self.confirmed_ready.count() != self.max_players:
#             raise ValueError("Not all players are ready.")
#         self.status = 'ongoing'
#         self.start_date = timezone.now()
#         self.save()

#     def end_tournament(self):
#         self.status = 'completed'
#         self.end_date = timezone.now()
#         self.save()
