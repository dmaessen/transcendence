from django.db import models

# IS THIS NECESSARY WHEN WE HAVE PlayerQueue class?

#this player will be a replacement to Django's default User model, 
# User model is managed by the authentication system.
#When to Use Django's User Model:
# You would use the User model in cases where your application requires:
# Authentication: If your app needs users to log in or register.
# Personalization: If you want to associate data with specific users (e.g., their settings, preferences, or history).
# Authorization: If you need to implement roles (e.g., admin, staff, user) or restrict access to certain features or views.

# class Player(models.Model):
#     username = models.CharField(max_length=255)
#     skill_level = models.IntegerField()

    #meta will be on when postgres comes in play
    # class Meta:
    #     managed = False  # django won't manage the external database's schema
    #     db_table = 'postgres_player_table'

class PlayerQueue(models.Model):
    """
    Respresents each player waiting to be matched
    """
    player_id = models.CharField(max_length=255, unique=True)
    #skill_level = models.IntegerField()  
    total_wins = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Player {self.player_id} (Skill: {self.skill_level})"

class Match(models.Model):
    """
    A single game with matched 2 players
    """
    player1 = models.CharField(max_length=255)
    player2 = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    winner = models.CharField(max_length=255, null=True, blank=True)
    result = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Match: {self.player1} vs {self.player2}"

# null=true -> can have "NULL" in the database.
# blank=true -> will not require the field to have a value during validation

# class Tournament(models.Model):
#     """
#     Respresents a tournament with multiple matches
#     """
#     name = models.CharField(max_length=255, unique=True)
#     number_of_players = models.IntegerField(default=0)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField(null=True, blank=True)
#     winner = models.CharField(max_length=255, null=True, blank=True)