import json
import random
import math
from game_server.game_logic import Game  # import the normal game logic to use in individual matches

class Tournament:
    def __init__(self, mode):
        self.mode = mode  # Either "4-player" or "8-player"
        self.num_players = mode
        self.players = []  # List of player IDs
        self.matches = []  # Store ongoing matches
        self.bracket = {}  # Stores matchups for each round -- GUL??
        self.current_round = 1
        self.running = False
        self.winners = []  # Players who win their matches
        self.final_winner = None

    def add_player(self, player_id):
        if len(self.players) < self.num_players:
            self.players.append(player_id)
            print(f"Player {player_id} joined the tournament.", flush=True)
        else:
            print(f"Tournament is full. Player {player_id} cannot join.", flush=True) # do something extra??

    def start_tournament(self):
        if len(self.players) != self.num_players:
            print("Not enough players to start the tournament.", flush=True)
            return

        self.running = True
        self._create_bracket() # look into this 
        self._start_next_round() # look into this

    def _create_bracket(self): # look into this -- gul??
        """Creates the tournament bracket by pairing up players."""
        random.shuffle(self.players)
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
            match = Game("Two Players (remote)")
            match.add_player(player1)
            match.add_player(player2)
            match.start_game()
            self.matches.append((player1, player2, match))

        print(f"Round {self.current_round} started with {len(self.matches)} matches.", flush=True)

    def update_match(self, player1, player2, winner):
        """Updates the tournament after a match is completed."""
        self.winners.append(winner)

        # rm the finished match
        self.matches = [(p1, p2, g) for p1, p2, g in self.matches if p1 != player1 and p2 != player2]

        if len(self.matches) == 0:  # all matches in this round are completed
            self._advance_to_next_round()

    def _advance_to_next_round(self):
        """Advances to the next round with the winners."""
        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner}", flush=True)
            return

        self.current_round += 1
        self.bracket[self.current_round] = [
            (self.winners[i], self.winners[i + 1]) for i in range(0, len(self.winners), 2)
        ]

        self._start_next_round()

    def get_tournament_state(self):
        return {
            "players": self.players,
            "bracket": self.bracket,
            "current_round": self.current_round,
            "running": self.running,
            "final_winner": self.final_winner
        }
