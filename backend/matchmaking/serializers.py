from rest_framework import serializers
from .models import PlayerQueue, Match

class PlayerQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerQueue
        fields = ['player_id', 'total_wins', 'joined_at', 'is_active']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['player1', 'player2', 'started_at', 'completed_at', 'winner', 'result' ]
