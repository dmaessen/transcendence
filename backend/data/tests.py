import os
import csv
from django.test import TestCase
from .models import CustomUser, Match, Tournament
from datetime import timedelta
from datetime import datetime
from django.db.models import Q

class ModelFromFileTest(TestCase):
    def print_users_table(self):
        users = CustomUser.objects.all()
        print(f"{'ID':<5} {'Name':<15} {'Location':<20} {'Score':<10} {'Victories':<10} {'Tournaments':<20}")
        print("=" * 60)
        for user in users:
            tournament_ids = ", ".join(str(t.id) for t in user.tournaments.all())
            # Filter matches where the player is the winner and count
            wins = Match.objects.filter(winner=user)
            win_count = wins.count()

            # Filter matches with the player and calculate score
            matches = Match.objects.filter(Q(player_1=user) | Q(player_2=user))
            matches_count = matches.count()
            if matches_count != 0 : 
                score = win_count / matches_count
            else:
                score = 0
            print(f"{user.id:<5} {user.name:<15} {user.location:<20} {score:<10.2f} {win_count:<10} {tournament_ids:<20}")
        print("\n")

    def print_match_table(self):
        matches = Match.objects.all()
        print(f"{'p1':<15} {'p2':<15} {'p1_points':<5} {'p2_points':<5} {'time':<10} {'winner_id':<5} {'winner_name':<20} {'tournament':<20}")
        print("=" * 100)
        for matchs in matches:
            # Calculate total time in minutes and seconds
            total_seconds = int(matchs.match_time.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            match_time_str = f"{minutes}m {seconds}s"
            # Get tournament ID or display 'N/A' if no tournament is associated
            tournament_id = matchs.tournament.id if matchs.tournament else "N/A"
            print(f"{matchs.player_1.name:<15} {matchs.player_2.name:<15} {matchs.player_1_points:<5} {matchs.player_2_points:<5} {match_time_str:<10} {matchs.winner.id:<5} {matchs.winner.name:<20} {tournament_id:<15}")
        print("\n")

    def setUp(self):
        # Set up user data
        self.setUpUsers()
        # Set up matches after users are created
        self.setUpMatches()
        # Set up tournaments after users and matches
        self.setUpTournaments()

    def setUpUsers(self):
        # Path to your test file
        self.file_path = '/app/data/test_data/users.csv'
        # Read the CSV file and create users
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            self.csv_users = [row for row in reader]
            for row in self.csv_users:
                CustomUser.objects.create(
                    name=row['name'],
                    location=row['location'],
                )
        print(f"Users were set and {CustomUser.objects.count()} users have been created!")
        # self.print_users_table()

    def test_users_created(self):
        print("Testing users table\n")
        # Verify the total number of users matches the CSV
        self.assertEqual(CustomUser.objects.count(), len(self.csv_users))

        # Validate each user's data
        for csv_user in self.csv_users:
            user = CustomUser.objects.get(name=csv_user['name'])
            self.assertEqual(user.location, csv_user['location'])

        print("All users validated successfully.")

    def setUpMatches(self):
        # Retrieve the users needed for the matches
        self.user1 = CustomUser.objects.get(name=self.csv_users[0]['name'])
        self.user2 = CustomUser.objects.get(name=self.csv_users[1]['name'])
        self.user3 = CustomUser.objects.get(name=self.csv_users[2]['name'])
        self.user4 = CustomUser.objects.get(name=self.csv_users[3]['name'])
        self.user5 = CustomUser.objects.get(name=self.csv_users[4]['name'])
        self.user6 = CustomUser.objects.get(name=self.csv_users[5]['name'])
        self.user7 = CustomUser.objects.get(name=self.csv_users[6]['name'])
        self.user8 = CustomUser.objects.get(name=self.csv_users[7]['name'])
        self.user9 = CustomUser.objects.get(name=self.csv_users[8]['name'])

        # Create match entries
        Match.objects.create(
            player_1=self.user1,
            player_2=self.user5,
            player_1_points=3,
            player_2_points=5,
            match_time=timedelta(minutes=2),
            winner=self.user5
        )
        Match.objects.create(
            player_1=self.user3,
            player_2=self.user6,
            player_1_points=7,
            player_2_points=8,
            match_time=timedelta(minutes=3),
            winner=self.user6
        )
        Match.objects.create(
            player_1=self.user7,
            player_2=self.user2,
            player_1_points=6,
            player_2_points=10,
            match_time=timedelta(minutes=2),
            winner=self.user2
        )
        Match.objects.create(
            player_1=self.user4,
            player_2=self.user8,
            player_1_points=7,
            player_2_points=8,
            match_time=timedelta(minutes=3),
            winner=self.user8
        )
        Match.objects.create(
            player_1=self.user5,
            player_2=self.user6,
            player_1_points=7,
            player_2_points=10,
            match_time=timedelta(minutes=2),
            winner=self.user6
        )
        Match.objects.create(
            player_1=self.user2,
            player_2=self.user8,
            player_1_points=7,
            player_2_points=8,
            match_time=timedelta(minutes=3),
            winner=self.user8
        )
        Match.objects.create(
            player_1=self.user2,
            player_2=self.user6,
            player_1_points=7,
            player_2_points=10,
            match_time=timedelta(minutes=2),
            winner=self.user6
        )
        Match.objects.create(
            player_1=self.user6,
            player_2=self.user8,
            player_1_points=7,
            player_2_points=8,
            match_time=timedelta(minutes=3),
            winner=self.user8
        )
        Match.objects.create(
            player_1=self.user4,
            player_2=self.user6,
            player_1_points=7,
            player_2_points=10,
            match_time=timedelta(minutes=2),
            winner=self.user6
        )
        Match.objects.create(
            player_1=self.user9,
            player_2=self.user8,
            player_1_points=7,
            player_2_points=8,
            match_time=timedelta(minutes=3),
            winner=self.user8
        )
        Match.objects.create(
            player_1=self.user9,
            player_2=self.user5,
            player_1_points=7,
            player_2_points=10,
            match_time=timedelta(minutes=2),
            winner=self.user5
        )
        print(f"Matches is set and {Match.objects.count()} matches have been created!")
        # self.print_match_table()

    def test_matches_created(self):
        print("Testing matches tables\n")
        # Verify the total number of matches created
        self.assertEqual(Match.objects.count(), 11)

        # Validate match data
        match1 = Match.objects.get(player_1=self.user1, player_2=self.user5)
        self.assertEqual(match1.player_1_points, 3)
        self.assertEqual(match1.player_2_points, 5)
        self.assertEqual(match1.winner, self.user5)

        match2 = Match.objects.get(player_1=self.user3, player_2=self.user6)
        self.assertEqual(match2.player_1_points, 7)
        self.assertEqual(match2.player_2_points, 8)
        self.assertEqual(match2.winner, self.user6)

        match3 = Match.objects.get(player_1=self.user7, player_2=self.user2)
        self.assertEqual(match3.player_1_points, 6)
        self.assertEqual(match3.player_2_points, 10)
        self.assertEqual(match3.winner, self.user2)

        match4 = Match.objects.get(player_1=self.user4, player_2=self.user8)
        self.assertEqual(match4.player_1_points, 7)
        self.assertEqual(match4.player_2_points, 8)
        self.assertEqual(match4.winner, self.user8)

        match5 = Match.objects.get(player_1=self.user5, player_2=self.user6)
        self.assertEqual(match5.player_1_points, 7)
        self.assertEqual(match5.player_2_points, 10)
        self.assertEqual(match5.winner, self.user6)

        match6 = Match.objects.get(player_1=self.user2, player_2=self.user8)
        self.assertEqual(match6.player_1_points, 7)
        self.assertEqual(match6.player_2_points, 8)
        self.assertEqual(match6.winner, self.user8)

        match7 = Match.objects.get(player_1=self.user2, player_2=self.user6)
        self.assertEqual(match7.player_1_points, 7)
        self.assertEqual(match7.player_2_points, 10)
        self.assertEqual(match7.winner, self.user6)

        print("All matches validated successfully.\n")
        # print("Final tables")

    def setUpTournaments(self):
        # Set tournament start and end times for today
        start_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)  # 1-hour tournament duration

        # Create the tournament
        self.tournament = Tournament.objects.create(
        number_of_players=8,
        start_date=start_time,
        end_date=end_time
        )

        # Retrieve the matches in the correct sequence
        match1 = Match.objects.get(player_1=self.user1, player_2=self.user5)
        match2 = Match.objects.get(player_1=self.user3, player_2=self.user6)
        match3 = Match.objects.get(player_1=self.user7, player_2=self.user2)
        match4 = Match.objects.get(player_1=self.user4, player_2=self.user8)
        match5 = Match.objects.get(player_1=self.user5, player_2=self.user6)
        match6 = Match.objects.get(player_1=self.user2, player_2=self.user8)
        match7 = Match.objects.get(player_1=self.user2, player_2=self.user6)

        # Assign matches to the tournament
        for match in [match1, match2, match3, match4, match5, match6, match7]:
            match.tournament = self.tournament
            match.save()

        # Add players to the tournament
        players = [self.user1, self.user3, self.user7, self.user4, self.user5, self.user6, self.user2, self.user8]
        for player in players:
            player.tournaments.add(self.tournament)
            player.save()

        # Update tournament results
        self.tournament.first_place = self.user6
        self.tournament.second_place = self.user2
        self.tournament.third_place = self.user8
        self.tournament.fourth_place = self.user5
        self.tournament.save()

        print(f"Tournament is set and {Tournament.objects.count()} tournaments have been created!")        

    def test_tournaments(self):
        print("Testing tournamnets\n")
        # Retrieve all tournaments
        tournaments = Tournament.objects.all()

        # Check that tournaments exist
        self.assertGreater(tournaments.count(), 0, "No tournaments found.")

        for tournament in tournaments:
            print(f"Testing Tournament {tournament.id}...")

            # Verify the start and end dates are valid
            self.assertIsNotNone(tournament.start_date, f"Tournament {tournament.id} has no start date.")
            self.assertIsNotNone(tournament.end_date, f"Tournament {tournament.id} has no end date.")
            self.assertLess(
                tournament.start_date,
                tournament.end_date,
                f"Tournament {tournament.id} has an invalid date range."
            )

            # Verify that the correct number of matches are assigned
            matches = Match.objects.filter(tournament=tournament)
            self.assertGreater(matches.count(), 0, f"No matches found for Tournament {tournament.id}.")

            # Verify the players in the tournament
            players = tournament.players.all()
            self.assertGreater(players.count(), 0, f"No players found for Tournament {tournament.id}.")

            # Check that the matches involve only players in the tournament
            for match in matches:
                self.assertIn(match.player_1, players, f"Player {match.player_1} is not part of Tournament {tournament.id}.")
                self.assertIn(match.player_2, players, f"Player {match.player_2} is not part of Tournament {tournament.id}.")

            # Check that the winner is correctly assigned for matches
            for match in matches:
                self.assertIsNotNone(match.winner, f"Match {match.id} in Tournament {tournament.id} has no winner.")
                self.assertIn(match.winner, players, f"Winner {match.winner} of Match {match.id} is not part of Tournament {tournament.id}.")

            # Print tournament details
            print(f"Tournament {tournament.id} passed all tests.")

        print("All tournaments validated successfully.")

    def test_overall(self):
        print("Testing overall tournament and match data...\n")

        # Check how many matches belong to each tournament
        tournaments = Tournament.objects.all()
        for tournament in tournaments:
            matches = Match.objects.filter(tournament=tournament)
            print(f"Tournament {tournament.id} has {matches.count()} matches.")
            self.assertGreater(matches.count(), 0, f"Tournament {tournament.id} has no matches.")

        # Check how many tournaments each user has joined
        users = CustomUser.objects.all()
        for user in users:
            tournaments_joined = user.tournaments.count()
            print(f"User {user.name} ({user.id}) has joined {tournaments_joined} tournaments.")
            self.assertGreaterEqual(tournaments_joined, 0, f"User {user.name} ({user.id}) has invalid tournament count.")

        # Verify the total number of matches in each tournament
        for tournament in tournaments:
            matches = Match.objects.filter(tournament=tournament)
            players = tournament.players.all()
            print(f"Tournament {tournament.id} involves {players.count()} players and {matches.count()} matches.")
            self.assertGreater(players.count(), 0, f"Tournament {tournament.id} has no players.")
            self.assertGreater(matches.count(), 0, f"Tournament {tournament.id} has no matches.")

            # Validate matches involve only players from the tournament
            for match in matches:
                self.assertIn(match.player_1, players, f"Match {match.id}: Player 1 ({match.player_1}) is not part of Tournament {tournament.id}.")
                self.assertIn(match.player_2, players, f"Match {match.id}: Player 2 ({match.player_2}) is not part of Tournament {tournament.id}.")

        print("Overall tests passed successfully.\n")
        print("Here are ze tables\n")
        self.print_users_table()
        self.print_match_table()