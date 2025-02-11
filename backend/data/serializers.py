from rest_framework import serializers
from data.models import User, Match, Tournament
import logging

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
            'player_1_name',
            'player_2_name',
            'player_1_points',
            'player_2_points',
            'match_start',
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

class MatchSummarySerializer(serializers.ModelSerializer):
    opponent = serializers.SerializerMethodField()  # Dynamically get the opponent's name
    logging.info(f"Request {opponent}")
    class Meta:
        model = Match
        fields = ["match_start", "winner", "opponent"]

    def get_opponent(self, obj):
        """Return the name of the opponent, assuming 'request.user' is player_1 or player_2."""
        user = self.context.get("user")
        if user:
            return obj.player_1.name if obj.player_2 == user else obj.player_2.name
        return "Unknown"

class TournamentSummarySerializer(serializers.ModelSerializer):
    winner = serializers.ReadOnlyField(source="first_place.name")  # Only show the winner
    logging.info(f"winner: {winner}")
    start_date = serializers.DateTimeField()
    # logging.info(f"start_date: {start_date}")
    class Meta:
        model = Tournament
        fields = ["start_date", "winner"]
