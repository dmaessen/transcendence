from rest_framework import serializers
from data.models import CustomUser, Match, Tournament
import logging

logger = logging.getLogger(__name__)

class MySerializer(serializers.Serializer):
    def validate(self, data):
        logger.debug("This is a debug message from serializers.py")
        logger.info(f"Validating data: {data}")
        return data

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
    opponent = serializers.SerializerMethodField()
    winner_name = serializers.CharField(source='winner.username')
    
    class Meta:
        model = Match
        fields = ["match_start", "winner_name", "opponent"]

    def get_opponent(self, obj):
        """Return the name of the opponent."""
        user = self.context.get("user")
        if user:
            opponent = obj.player_1.name if obj.player_2 == user else obj.player_2.name
            logger.info(f"Opponent: {opponent}")  # Log the opponent here
            return opponent
        return "Unknown"
    


class TournamentSummarySerializer(serializers.ModelSerializer):
    winner = serializers.ReadOnlyField(source="first_place.name")
    start_date = serializers.DateTimeField()

    class Meta:
        model = Tournament
        fields = ["start_date", "winner"]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     logger.info(f"Tournament winner: {self.validated_data.get('winner', 'Unknown')}")
