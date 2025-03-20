import json
import random
import math
import asyncio
from game_server.game_logic import Game  # import the normal game logic to use in individual matches
from channels.layers import get_channel_layer

class Tournament:
    _instance = None

    def __new__(cls, mode):
        if cls._instance is None:
            cls._instance = super(Tournament, cls).__new__(cls)
            cls._instance._initialized = False  # prevents reinitilizing
        return cls._instance

    def __init__(self, mode):
        if self._initialized:
            return
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
        self._initialized = True

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

    # def register_match_result(self, game_id, winner_username):
    #     winner = next((player for player in self.players if player["username"] == winner_username), None)
    #     # winner_id = winner["id"] # needed??
    #     if winner:
    #         self.winners.append(winner)
    #         print(f"SUCCESS WINNER APPENDED ")

    #     # if self.current_round not in self.bracket:
    #     #     return

    #     if str(self.current_round) in self.bracket:
    #         for match in self.bracket[str(self.current_round)]:
    #             if match[0]["player"]["username"] == winner_username:
    #                 match[0]["winner"] = True
    #                 match[1]["winner"] = False
    #             elif match[1]["player"]["username"] == winner_username:
    #                 match[0]["winner"] = False
    #                 match[1]["winner"] = True
    #             print(f"DONE ADDING TRUE:FALSE TO THE MATCH WINNER", flush=True)

    #     # rm the finished match based on game_id
    #     self.matches = [(g_id, p1, p2) for g_id, p1, p2 in self.matches if g_id != game_id]

    #     if len(self.matches) == 0:
    #         print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)
    #         self._advance_to_next_round()

    async def register_match_result(self, game_id, winner_username):
        print(f"Registering match result: Game {game_id}, Winner {winner_username}", flush=True)
        
        # Check if this game_id already exists in the matches list
        match_indices = [i for i, (g_id, p1, p2) in enumerate(self.matches) if g_id == game_id]
        
        # If no match found, return
        if not match_indices:
            print(f"Game {game_id} not found in matches", flush=True)
            return
        
        # Get the first occurrence of the match (in case of duplicates)
        match_index = match_indices[0]
        game_id, player1, player2 = self.matches[match_index]
        
        # Find the winner player object
        winner_player = next((player for player in self.players if player["username"] == winner_username), None)
        if not winner_player:
            print(f"Player {winner_username} not found in players list", flush=True)
            return
        
        # Check if this winner is already in the winners list to avoid duplicates
        if not any(winner["id"] == winner_player["id"] and winner["username"] == winner_player["username"] 
                for winner in self.winners):
            self.winners.append(winner_player)
            print(f"✅ Added {winner_username} to winners list", flush=True)
        else:
            print(f"Player {winner_username} already in winners list", flush=True)
        
        # Update the bracket with winner information
        if str(self.current_round) in self.bracket:
            bracket_updated = False
            for match in self.bracket[str(self.current_round)]:
                # Check both player positions (first and second)
                if (match[0]["player"]["username"] == player1 and match[1]["player"]["username"] == player2) or \
                (match[0]["player"]["username"] == player2 and match[1]["player"]["username"] == player1):
                    
                    # Set winner flags based on who won
                    match[0]["winner"] = (match[0]["player"]["username"] == winner_username)
                    match[1]["winner"] = (match[1]["player"]["username"] == winner_username)
                    bracket_updated = True
                    print(f"Updated bracket for round {self.current_round}, match between {player1} and {player2}", flush=True)
                    break
            
            if not bracket_updated:
                print(f"Could not find match in bracket for {player1} vs {player2}", flush=True)
        
        # Remove ALL occurrences of this game_id from matches to prevent duplicates
        self.matches = [(g_id, p1, p2) for g_id, p1, p2 in self.matches if g_id != game_id]
        
        # Check if we need to advance to the next round
        if len(self.matches) == 0:
            print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)
            await self._advance_to_next_round()

    # def _advance_to_next_round(self):
    #     print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)

    #     if len(self.winners) == 1:
    #         self.final_winner = self.winners[0]
    #         self.running = False
    #         print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
    #         return

    #     # if self.current_round + 1 not in self.bracket: # store until we have two winners to be paired
    #     #     self.bracket[self.current_round + 1] = []
    #     # while len(self.winners) >= 2:
    #     #     player1 = self.winners.pop(0)
    #     #     player2 = self.winners.pop(0)
    #     #     self.bracket[self.current_round +1].append((player1, player2)) # creates matches
    #     # if len(self.winners) == 1: #then wait still
    #     #     return

    #     # self.current_round += 1
    #     # # self.bracket[self.current_round] = [
    #     # #     (self.winners[i], self.winners[i + 1]) for i in range(0, len(self.winners) - 1, 2)
    #     # # ]

    #     # self._start_next_round()

    #     if len(self.matches) == 0 and len(self.winners) >= 2:
    #     # Ensure we only move forward when matches are over and winners exist
    #         self.current_round += 1
    #         self.bracket[self.current_round] = []

    #         # Prepare for the next round by pairing winners for matches
    #         while len(self.winners) >= 2:
    #             player1 = self.winners.pop(0)
    #             player2 = self.winners.pop(0)
    #             # self.bracket[self.current_round].append((player1, player2))
    #             self.bracket[self.current_round].append(
    #                 ({"player": player1, "winner": False}, {"player": player2, "winner": False})
    #             )

    #         print(f"Round {self.current_round} created with {len(self.bracket[self.current_round])} matches.", flush=True)
    #         self._start_next_round()

    #     else:
    #         print("Waiting for more matches to complete before advancing.", flush=True)

    async def _advance_to_next_round(self):
        print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)
        # round_key = str(self.current_round)
        # if round_key in self.bracket:
        #     for match in self.bracket[round_key]:
        #         # Get the usernames of both players in this match
        #         player1_username = match[0]["player"]["username"]
        #         player2_username = match[1]["player"]["username"]
                
        #         # Check if either player is in the winners list
        #         player1_is_winner = any(w["username"] == player1_username for w in self.winners)
        #         player2_is_winner = any(w["username"] == player2_username for w in self.winners)
                
        #         # Update winner flags
        #         match[0]["winner"] = player1_is_winner
        #         match[1]["winner"] = player2_is_winner
                
        #         if player1_is_winner or player2_is_winner:
        #             print(f"Updated winner status for match {player1_username} vs {player2_username}", flush=True)

        # Check if we have a final winner
        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
            return
        
        # Only proceed if we have no matches and at least 2 winners
        if len(self.matches) == 0 and len(self.winners) >= 2:
            # Increment the round
            self.current_round += 1
            # Initialize the bracket for the new round
            self.bracket[str(self.current_round)] = []
            self.bracket[(self.current_round)] = []
            
            # Make a copy of the winners to work with
            round_participants = self.winners.copy()
            # Clear the winners list for the next round's winners
            #self.winners = []
            
            # Create matches from pairs of participants
            #self.matches = []
            #next_game_id = self._generate_next_game_id()  # You should have a method to generate unique game IDs
            
            # Pair players and create bracket entries
            while len(round_participants) >= 2:
                player1 = round_participants.pop(0)
                player2 = round_participants.pop(0)
                
                # Add to bracket
                self.bracket[str(self.current_round)].append(
                    ({"player": player1, "winner": False}, {"player": player2, "winner": False})
                )
                
                # Add to matches list
                # self.matches.append((next_game_id, player1["username"], player2["username"]))
                # next_game_id += 1  # Increment for next match
            
            print(f"Round {self.current_round} created with {len(self.bracket[str(self.current_round)])} matches.", flush=True)
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

    # def add_match(self, player1, player2, game_id):
    #     self.matches.append(({"player1": player1["id"], "player2": player2["id"]}, game_id))