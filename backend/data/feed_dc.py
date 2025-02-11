import os
import csv
import sys
from datetime import timedelta, datetime
from django.db import transaction


# Add the project root to the Python path
sys.path.append('/app')

# Set the environment variable to specify the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
# Initialize Django
django.setup()

from data.models import *

# Path to the CSV file
CSV_FILE_PATH = "/app/data/test_data/users.csv"

def create_users():
    """Reads users from CSV and adds them to the database."""
    with open(CSV_FILE_PATH, "r") as file:
        reader = csv.DictReader(file)
        users = [
            User(
                name=row["name"],
                location=row["location"],
                email=row["email"],
                username=row["username"],
                is_active=row["is_active"] == "True",
                is_staff=row["is_staff"] == "True",
                oauth_tokens=row["oauth_tokens"],
            )
            for row in reader
        ]
    User.objects.bulk_create(users)
    print(f"Created {len(users)} users")


def create_matches():
    """Creates match records using test users."""
    users = list(User.objects.all())

    if len(users) < 9:
        print("Not enough users to create matches")
        return

    date_match = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)

    matches = [
        Match(player_1=users[0], player_2=users[4], player_1_points=3, player_2_points=5, match_start=date_match, match_time=timedelta(minutes=2), winner=users[4]),
        Match(player_1=users[2], player_2=users[5], player_1_points=7, player_2_points=8, match_start=date_match, match_time=timedelta(minutes=3), winner=users[5]),
        Match(player_1=users[6], player_2=users[1], player_1_points=6, player_2_points=10, match_start=date_match, match_time=timedelta(minutes=2), winner=users[1]),
        Match(player_1=users[3], player_2=users[7], player_1_points=7, player_2_points=8, match_start=date_match, match_time=timedelta(minutes=3), winner=users[7]),
        Match(player_1=users[4], player_2=users[5], player_1_points=7, player_2_points=10, match_start=date_match, match_time=timedelta(minutes=2), winner=users[5]),
        Match(player_1=users[1], player_2=users[7], player_1_points=7, player_2_points=8, match_start=date_match, match_time=timedelta(minutes=3), winner=users[7]),
        Match(player_1=users[1], player_2=users[5], player_1_points=7, player_2_points=10, match_start=date_match, match_time=timedelta(minutes=2), winner=users[5]),
        Match(player_1=users[5], player_2=users[7], player_1_points=7, player_2_points=8, match_start=date_match, match_time=timedelta(minutes=3), winner=users[7]),
        Match(player_1=users[3], player_2=users[5], player_1_points=7, player_2_points=10, match_start=date_match, match_time=timedelta(minutes=2), winner=users[5]),
        Match(player_1=users[8], player_2=users[7], player_1_points=7, player_2_points=8, match_start=date_match, match_time=timedelta(minutes=3), winner=users[7]),
        Match(player_1=users[8], player_2=users[4], player_1_points=7, player_2_points=10, match_start=date_match, match_time=timedelta(minutes=2), winner=users[4]),
    ]

    Match.objects.bulk_create(matches)
    print(f"Created {len(matches)} matches")


def create_tournament():
    """Creates a tournament and assigns matches to it."""
    users = list(User.objects.all())
    matches = list(Match.objects.all())

    if len(users) < 8 or len(matches) < 7:
        print("Not enough users or matches to create a tournament")
        return

    start_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    tournament = Tournament.objects.create(
        max_players=8, start_date=start_time, end_date=end_time
    )

    # Assign matches to the tournament
    for match in matches[:7]:  # Select the first 7 matches
        match.tournament = tournament
        match.save()

    # Add players to the tournament
    players = users[:8]
    tournament.players.set(players)

    # Assign rankings
    tournament.first_place = users[5]
    tournament.second_place = users[1]
    tournament.third_place = users[7]
    tournament.fourth_place = users[4]
    tournament.save()

    print(f"Created tournament with {len(players)} players")


def main():
    """Runs the database setup in a transaction."""
    with transaction.atomic():
        create_users()
        create_matches()
        create_tournament()


if __name__ == "__main__":
    main()
