from rest_framework import serializers
from data.models import CustomUser, Match, Tournament

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'email',
            'name',
            'location',
            'oauth_tokens',
            'tournaments'
        ]

class MatchSerializer(serializers.ModelSerializer):
    player_1_name = serializers.ReadOnlyField(source='player_1.name')
    player_2_name = serializers.ReadOnlyField(source='player_2.name')

    class Meta:
        model = Match
        fields = [
            'id',
            'player_1',
            'player_2',
            'player_1_points',
            'player_2_points',
            'match_time',
            'winner',
            'tournament'
        ]

class TournamentSerializer(serializers.ModelSerializer):
    players = UserSerializer(many=True, read_only=True)
    first_place = UserSerializer(read_only=True)
    second_place = UserSerializer(read_only=True)
    third_place = UserSerializer(read_only=True)
    fourth_place = UserSerializer(read_only=True)
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id',
            'first_place',
            'second_place',
            'third_place',
            'fourth_place',
            'number_of_players',
            'start_date',
            'end_date',
            'players',
            'matches',
        ]