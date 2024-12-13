from django.db import models
from cryptography.fields import encrypt #should we use this?  it's available 


class User(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30, blank=True, null=True)
    score = models.IntegerField(default=0)
    victories = models.IntegerField(default=0)
    oauth_tokens = encrypt(models.JSONField(null=True, blank=True))

    def __str__(self):
        return self.name


class Match(models.Model):
    player_1 = models.ForeignKey(User, related_name="player_1_matches", on_delete=models.SET_NULL, null=True)
    player_2 = models.ForeignKey(User, related_name="player_2_matches", on_delete=models.SET_NULL, null=True)
    player_1_points = models.IntegerField(default=0)
    player_2_points = models.IntegerField(default=0)
    match_time = models.DateTimeField()
    winner = models.ForeignKey(User, related_name="matches_won", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Match: {self.player_1} vs {self.player_2}"


class Tournament(models.Model):
    MATCH_TYPES = [
        ("F", "Final"),
        ("S", "Semi-Final"),
        ("Q", "Quarter-Final"),
    ]
    match_type = models.CharField(max_length=1, choices=MATCH_TYPES)
    matches = models.ManyToManyField(Match, related_name="tournaments")

    def __str__(self):
        return f"Tournament: {self.get_match_type_display()}"
