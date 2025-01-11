from django.db import models
# from cryptography.fields import encrypt  # Assuming this is a custom field for encryption

from django.db import models

class User(models.Model):
    # Field for status
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30, blank=True, null=True)
    score = models.IntegerField(default=0)  # Ratio to rank people
    victories = models.IntegerField(default=0)
    oauth_tokens = models.JSONField(null=True, blank=True)  # Encrypting oauth tokens
    tournaments = models.ManyToManyField('Tournament', related_name='players', blank=True)  # Many-to-many relationship with Tournament

    def __str__(self):
        return self.name
    def clean(self):
        if self.score < 0:
            raise ValueError("Score cannot be negative.")
        if self.victories < 0:
            raise ValueError("Victories cannot be negative.")


class Match(models.Model):
    player_1 = models.ForeignKey(User, related_name="player_1_matches", on_delete=models.SET_NULL, null=True)
    player_2 = models.ForeignKey(User, related_name="player_2_matches", on_delete=models.SET_NULL, null=True)
    player_1_points = models.IntegerField(default=0)
    player_2_points = models.IntegerField(default=0)
    match_time = models.DateTimeField()
    winner = models.ForeignKey(User, related_name="matches_won", on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey('Tournament', related_name="matches", on_delete=models.SET_NULL, null=True, blank=True)  # Tournament for match, null if not part of any

    def __str__(self):
        return f"Match: {self.player_1} vs {self.player_2}"


class Tournament(models.Model):
    first_place = models.ForeignKey(User)
    second_place = models.ForeignKey(User)
    third_place = models.ForeignKey(User)
    fourth_place = models. ForeignKey(User)
    number_of_players = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Tournament: {self.get_match_type_display()}"


# Get all tournaments a player is in:
# player = User.objects.get(id=x)
# tournaments = player.tournaments.all()  # All tournaments the player is part of

# Get all players in a specific tournament:
# tournament = Tournament.objects.get(id=x)
# players = tournament.players.all()  # All players in this tournament

# Get all matches in a specific tournament:
# tournament = Tournament.objects.get(id=x)
# matches = tournament.matches.all()  # All matches in this tournament
