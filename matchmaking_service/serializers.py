from rest_framework import serializers
from .models import PlayerQueue, Match, MatchResult

class PlayerQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerQueue
        fields = ['player_id', 'skill_level', 'total_wins', 'joined_at']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['player1', 'player2', 'started_at', 'completed_at', 'winner' ]

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = ['match', 'winner', 'loser', 'completed_at']