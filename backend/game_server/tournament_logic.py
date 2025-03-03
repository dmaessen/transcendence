import json
import random
import math
from game_server.game_logic import Game  # import the normal game logic to use in individual matches

class Tournament:
    def __init__(self, mode):
        self.mode = mode  # Either "4-player" or "8-player"
        self.num_players = int(mode)  # Convert mode to an integer
        self.players = []  # List of dictionaries with player IDs and usernames
        self.matches = []  # Store ongoing matches
        self.bracket = {}  # Stores matchups for each round
        self.current_round = 1
        self.running = False
        self.winners = []  # Players who win their matches
        self.final_winner = None

    def add_player(self, player_id, username):
        if len(self.players) < self.num_players:
            self.players.append({"id": player_id, "username": username})
            print(f"Player {username} joined the tournament. Total players: {len(self.players)}", flush=True)
        else:
            print(f"Tournament is full. Player {username} cannot join.", flush=True)

    def start_tournament(self):
        if len(self.players) != self.num_players:
            print("Not enough players to start the tournament.", flush=True)
            return

        self.running = True
        self._create_bracket()
        self._start_next_round()

    def _create_bracket(self):
        """Creates the tournament bracket by pairing up players."""
        # random.shuffle(self.players)
        self.bracket[self.current_round] = [
            (self.players[i], self.players[i + 1]) for i in range(0, len(self.players), 2)
        ]
        print(f"Tournament bracket created: {self.bracket}", flush=True)

    def _start_next_round(self):
        if self.final_winner:
            print(f"Tournament already ended. Winner: {self.final_winner}", flush=True)
            return

        self.matches = []
        self.winners = []

        for player1, player2 in self.bracket[self.current_round]:
            #match = Game("Two Players (remote)") # works
            match = Game(self.mode)
            match.add_player(player1["id"], player1["username"])
            match.add_player(player2["id"], player2["username"])
            match.start_game()
            self.matches.append((player1, player2, match))

        print(f"Round {self.current_round} started with {len(self.matches)} matches.", flush=True)

    def update_match(self, player1_id, player2_id, winner_id):
        """Updates the tournament after a match is completed."""
        winner = next(player for player in self.players if player["id"] == winner_id)
        self.winners.append(winner)

        # Remove the finished match
        self.matches = [(p1, p2, g) for p1, p2, g in self.matches if p1["id"] != player1_id and p2["id"] != player2_id]

        if len(self.matches) == 0:  # All matches in this round are completed
            self._advance_to_next_round()

    def _advance_to_next_round(self):
        """Advances to the next round with the winners."""
        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
            return

        self.current_round += 1
        self.bracket[self.current_round] = [
            (self.winners[i], self.winners[i + 1]) for i in range(0, len(self.winners), 2)
        ]

        self._start_next_round()

    def get_tournament_state(self):
        return {
            "mode": self.mode,
            "num_players": self.num_players,
            "players": self.players,
            "bracket": self.bracket,
            "current_round": self.current_round,
            "tournament_active": self.running,
            "running": self.running,
            "final_winner": self.final_winner,
            "matches": self.matches,
            "winners": self.winners,
            "players_in": len(self.players),
            "remaining_spots": self.num_players - len(self.players),
        }

    def get_tournamentstate(self):
        return {
            "mode": self.mode,
            "num_players": self.num_players,
            "players": self.players,
            "bracket": self.bracket,
            "current_round": self.current_round,
            "tournament_active": self.running,
            "running": self.running,
            "final_winner": self.final_winner,
            "winners": self.winners,
            "players_in": len(self.players),
            "remaining_spots": self.num_players - len(self.players),
            "matches": [
                    {
                        "player1": match[0],
                        "player2": match[1],
                        "game_state": match[2].get_state()  # Extract state instead of raw object
                    }
                    for match in self.matches
                ],
        }