from django.db import models


class PlayerQueue(models.Model):
    player_id = models.CharField(max_length=255)  # Unique identifier from User Service
    skill_level = models.IntegerField()  # Could represent ELO or similar ranking
    total_wins = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Player {self.player_id} (Skill: {self.skill_level})"

class Match(models.Model):
    player1 = models.CharField(max_length=255)
    player2 = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    winner = models.CharField(max_length=255, null=True, blank=True)  # Optional, updated later

    def __str__(self):
        return f"Match: {self.player1} vs {self.player2}"

class MatchResult(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result')
    winner = models.CharField(max_length=255)
    loser = models.CharField(max_length=255)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Winner: {self.winner}, Loser: {self.loser}"
