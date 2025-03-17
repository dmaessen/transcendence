import json
import random
import math
import asyncio
from game_server.game_logic import Game  # import the normal game logic to use in individual matches
from channels.layers import get_channel_layer

class Tournament:
    def __init__(self, mode):
        self.mode = mode
        self.num_players = int(mode)
        self.players = []  # player IDs and usernames
        self.matches = []  # ongoing matches
        self.bracket = {}  # matchups for each round -- THIS SEND TO LAURA
        self.current_round = 1
        self.running = False
        self.winners = []  # players who won their matches
        self.final_winner = None
        # self.room_name = None # for channel layer comm

    def add_player(self, player_id, username):
        if len(self.players) < self.num_players:
            self.players.append({"id": player_id, "username": username})
            print(f"Player {username} joined the tournament. Total players: {len(self.players)}", flush=True)
        else:
            print(f"Tournament is full. Player {username} cannot join.", flush=True)

    async def start_tournament(self):
        if len(self.players) != self.num_players:
            print("Not enough players to start the tournament.", flush=True)
            return

        self.running = True
        self._create_bracket()
        await self._start_next_round()

    def _create_bracket(self):
        # random.shuffle(self.players)
        # self.bracket[self.current_round] = [
        #     (self.players[i], self.players[i + 1]) for i in range(0, len(self.players), 2)
        # ]
        if self.current_round not in self.bracket:
            self.bracket[self.current_round] = []

        self.bracket[self.current_round] = [
            ({"player": self.players[i], "winner": False}, 
            {"player": self.players[i + 1], "winner": False}) 
            for i in range(0, len(self.players), 2)
        ]

        print(f"tournament bracket created: {self.bracket}", flush=True)

    async def _start_next_round(self):
        if self.final_winner:
            print(f"tournament already ended. Winner: {self.final_winner}", flush=True)
            return

        self.matches = []
        self.winners = []
        channel_layer = get_channel_layer()

        # if self.current_round not in self.bracket:
        #     return

        for player1, player2 in self.bracket[self.current_round]:
            ##match = Game("Two Players (remote)") # works
            # match = Game(self.mode)
            # match.add_player(player1["id"], player1["username"])
            # match.add_player(player2["id"], player2["username"])
            # match.start_game()
            # self.matches.append((player1, player2, match))
            match_exists = any(match["player1"] == player1["player"]["id"] and match["player2"] == player2["player"]["id"] for match in self.matches)
            if not match_exists:
                await channel_layer.group_send(
                    "tournament_lobby",
                    {
                        "type": "create.game.tournament",
                        "player1": player1["player"]["id"],
                        "player2": player2["player"]["id"],
                    }
                )
                print(f"Sent create.game.tournament message for {player1['player']['username']} vs {player2['player']['username']}", flush=True)
                # self.matches.append({"player1": player1["id"], "player2": player2["id"]})

        # print(f"Round {self.current_round} started with {len(self.matches)} matches.", flush=True)
        print(f"Round {self.current_round} started.", flush=True)

    def register_match_result(self, game_id, winner_username):
        winner = next((player for player in self.players if player["username"] == winner_username), None)
        # winner_id = winner["id"] # needed??
        if winner:
            self.winners.append(winner)
            print(f"SUCCESS WINNER APPENDED")

        # if self.current_round not in self.bracket:
        #     return

        if str(self.current_round) in self.bracket:
            for match in self.bracket[str(self.current_round)]:
                if match[0]["player"]["username"] == winner_username:
                    match[0]["winner"] = True
                    match[1]["winner"] = False
                elif match[1]["player"]["username"] == winner_username:
                    match[0]["winner"] = False
                    match[1]["winner"] = True
                print(f"DONE ADDING TRUE:FALSE TO THE MATCH WINNER", flush=True)

        # rm the finished match based on game_id
        self.matches = [(g_id, p1, p2) for g_id, p1, p2 in self.matches if g_id != game_id]

        if len(self.matches) == 0:
            self._advance_to_next_round()

    def _advance_to_next_round(self):
        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
            return

        # if self.current_round + 1 not in self.bracket: # store until we have two winners to be paired
        #     self.bracket[self.current_round + 1] = []
        # while len(self.winners) >= 2:
        #     player1 = self.winners.pop(0)
        #     player2 = self.winners.pop(0)
        #     self.bracket[self.current_round +1].append((player1, player2)) # creates matches
        # if len(self.winners) == 1: #then wait still
        #     return

        # self.current_round += 1
        # # self.bracket[self.current_round] = [
        # #     (self.winners[i], self.winners[i + 1]) for i in range(0, len(self.winners) - 1, 2)
        # # ]

        # self._start_next_round()

        if len(self.matches) == 0 and len(self.winners) >= 2:
        # Ensure we only move forward when matches are over and winners exist
            self.current_round += 1
            self.bracket[self.current_round] = []

            # Prepare for the next round by pairing winners for matches
            while len(self.winners) >= 2:
                player1 = self.winners.pop(0)
                player2 = self.winners.pop(0)
                self.bracket[self.current_round].append((player1, player2))
            
            print(f"Round {self.current_round} created with {len(self.bracket[self.current_round])} matches.", flush=True)
            self._start_next_round()

        else:
            print("Waiting for more matches to complete before advancing.", flush=True)

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

    # def add_match(self, player1, player2, game_id):
    #     self.matches.append(({"player1": player1["id"], "player2": player2["id"]}, game_id))