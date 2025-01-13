from django.db import models
# from cryptography.fields import encrypt  # Assuming this is a custom field for encryption

class User(models.Model):
    # Field for status
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30, blank=True, null=True)
    #score = models.IntegerField(default=0)  # Ratio to rank people can be calculated rertrieving data from the tables
    #victories = models.IntegerField(default=0) #This can be retrived from serching on the matches table
    oauth_tokens = models.JSONField(null=True, blank=True)  # Encrypting oauth tokens
    tournaments = models.ManyToManyField('Tournament', related_name='players', blank=True)  # Many-to-many relationship with Tournament

    def _str_(self):
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
    match_time = models.DurationField()
    winner = models.ForeignKey(User, related_name="match_winner", on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey('Tournament', related_name="matches", on_delete=models.SET_NULL, null=True, blank=True)  # Tournament for match, null if not part of any

    def _str_(self):
        return f"Match: {self.player_1} vs {self.player_2}"


class Tournament(models.Model):
    first_place = models.ForeignKey(User, related_name="first_place", on_delete=models.SET_NULL, null=True, blank=True)
    second_place = models.ForeignKey(User, related_name="second_place", on_delete=models.SET_NULL, null=True, blank=True)
    third_place = models.ForeignKey(User, related_name="third_place", on_delete=models.SET_NULL, null=True, blank=True)
    fourth_place = models. ForeignKey(User, related_name="fourth_place", on_delete=models.SET_NULL, null=True, blank=True)
    number_of_players = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def _str_(self):
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