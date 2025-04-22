import json
import random
import math
import asyncio
from channels.layers import get_channel_layer

class TournamentLogic:
    _instance = None

    def __new__(cls, mode):
        if cls._instance is None:
            cls._instance = super(Tournament, cls).__new__(cls)
            cls._instance._initialized = False  # prevents reinitilizing
        return cls._instance

    def __init__(self, mode):
        # if self._initialized:
        #     return
        self.mode = mode
        self.num_players = int(mode)
        self.players = []  # player IDs and usernames
        self.matches = []  # ongoing matches
        self.bracket = {}  # matchups for each round -- THIS SEND TO LAURA
        self.current_round = 1
        self.running = False
        self.winners = []  # players who won their matches
        self.final_winner = None
        # self._initialized = True

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
        print(f"NEW ROUND IN START NEXT ROUND", flush=True)
        if self.final_winner:
            print(f"tournament already ended. Winner: {self.final_winner}", flush=True)
            return

        self.matches = []
        self.winners = []
        channel_layer = get_channel_layer()

        for player1, player2 in self.bracket[self.current_round]:
            match_exists = any(match["player1"] == player1["player"]["id"] and match["player2"] == player2["player"]["id"] for match in self.matches)
            
            # WORK ON THIS
            # if player1["player"]["username"] == "wildcard":
            #     # then no need to start match as then other player is the winner directly
            # if player2["player"]["username"] == "wildcard":
            #     # then no need to start match as then other player is the winner directly
            
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

    async def register_match_result(self, game_id, winner_username):
        print(f"Registering match result: Game {game_id}, Winner {winner_username}", flush=True)
        
        match_indices = [i for i, (g_id, p1, p2) in enumerate(self.matches) if g_id == game_id]
        if not match_indices:
            print(f"Game {game_id} not found in matches", flush=True)
            return
        
        match_index = match_indices[0]
        game_id, player1, player2 = self.matches[match_index]
        
        winner_player = next((player for player in self.players if player["username"] == winner_username), None)
        if not winner_player:
            print(f"Player {winner_username} not found in players list", flush=True)
            return
        if not any(winner["id"] == winner_player["id"] and winner["username"] == winner_player["username"] 
                for winner in self.winners):
            self.winners.append(winner_player)
            print(f"✅ Added {winner_username} to winners list", flush=True)
        else:
            print(f"Player {winner_username} already in winners list", flush=True)
        
        # update bool with the winner of the match
        if self.current_round in self.bracket:
            bracket_updated = False
            for i, match in enumerate(self.bracket[self.current_round]):
                match = list(match)
                if (match[0]["player"]["username"] == player1 and match[1]["player"]["username"] == player2) or \
                (match[0]["player"]["username"] == player2 and match[1]["player"]["username"] == player1):
                    match[0]["winner"] = (match[0]["player"]["username"] == winner_username)
                    match[1]["winner"] = (match[1]["player"]["username"] == winner_username)
                    self.bracket[self.current_round][i] = tuple(match)
                    bracket_updated = True
                    print(f"Updated bracket for round {self.current_round}, match between {player1} and {player2}", flush=True)
                    break
            
            if not bracket_updated:
                print(f"Could not find match in bracket for {player1} vs {player2}", flush=True)
        
        # rm previous matches 
        self.matches = [(g_id, p1, p2) for g_id, p1, p2 in self.matches if g_id != game_id]
         
        if len(self.matches) == 0:
            await self._advance_to_next_round()

    async def _advance_to_next_round(self):
        print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)
        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
            # await channel_layer.group_send(
            #         "tournament_lobby",
            #         {
            #             "type": "disconnect",
            #         }
            #     )
            return

        if len(self.matches) == 0 and len(self.winners) >= 2:
            self.current_round += 1
            self.bracket[self.current_round] = []
            round_participants = self.winners.copy()

            while len(round_participants) >= 2:
                player1 = round_participants.pop(0)
                player2 = round_participants.pop(0)
                
                self.bracket[self.current_round].append(
                    ({"player": player1, "winner": False}, {"player": player2, "winner": False})
                )
            
            print(f"Round {self.current_round} created with {len(self.bracket[self.current_round])} matches.", flush=True)
            await self._start_next_round()

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

    # def reset_tournament(self, mode):
    #     self.mode = 4
    #     self.players = {}
    #     self.ready_players.clear()
    #     self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4, "speed": 4}
    #     self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
    #     self.score = {"player": 0, "opponent": 0}
    #     self.running = False
    #     self.partOfTournament = False
    #     self.mode = mode
    #     self.num_players = int(mode)
    #     self.players = []  # player IDs and usernames
    #     self.matches = []  # ongoing matches
    #     self.bracket = {}  # matchups for each round -- THIS SEND TO LAURA
    #     self.current_round = 1
    #     self.running = False
    #     self.winners = []  # players who won their matches
    #     self.final_winner = None
    #     # self.room_name = None # for channel layer comm
    #     self._initialized = True

