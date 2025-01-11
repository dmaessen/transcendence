from rest_framework import serializers
from data.models import User, Match

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'location', 'score', 'victories', 'oauth_tokens', 'tournaments']

class MatchSerializer(serializers.ModelSerializer):
    player_1_name = serializers.ReadOnlyField(source='player_1.name')
    player_2_name = serializers.ReadOnlyField(source='player_2.name')

    class Meta:
        model = Match
        fields = ['id', 'player_1', 'player_2', 'player_1_name', 'player_2_name', 
                  'player_1_points', 'player_2_points', 'match_time', 'winner', 'tournament']
