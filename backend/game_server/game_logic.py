# game_logic.py
# Backend logic for handling game state, including ball and paddle movements

import json
import random
import math

class Game:
    def __init__(self, mode):
        #self.id = None
        self.mode = mode
        self.width = 1400
        self.height = 1000
        self.players = {}  # Use a dictionary to store players by player_id
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4}
        self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
        self.score = {"player": 0, "opponent": 0}
        self.running = False
        self.status = None #default can be "waiting", "started"

    def add_player(self, player_id):
        if player_id not in self.players:
            if len(self.players) == 0: #first player
                self.players[player_id] = {"x": 20, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "player"}
                print(f"Player {player_id} added as Player 1.", flush=True)
            elif len(self.players) == 1: #second player
                self.players[player_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent"}
                print(f"Player {player_id} added as Player 2 (opponent).", flush=True)
            else:
                print(f"Cannot add more players. Maximum supported is 2.", flush=True)
            
            # if len(self.players) == 1:
            #     self.players[player_id]["role"] = "player"
            # elif len(self.players) == 2:
            #     self.players[player_id]["role"] = "opponent"
            #     print(f"Opponent assigned to Player {player_id}", flush=True)
        
        # automatically add a bot if only one player (in One Player mode)
        if self.mode == "One Player" and len(self.players) == 1:
            bot_id = "bot"
            self.players[bot_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent"}
            print(f"Bot added as opponent: {bot_id}", flush=True)

        if self.mode == "Two Players (hot seat)" and len(self.players) == 1:
            opponent_id = "opponent"
            self.players[opponent_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent"}
            print(f"Opponent added as opponent: {opponent_id}", flush=True) 

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            print(f"Player {player_id} removed.", flush=True)
            if len(self.players) == 0:
                self.running = False  # Stop game if no players are left

    def reset_game(self, mode):
        self.mode = mode
        self.players = {}
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4}
        self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
        self.score = {"player": 0, "opponent": 0}
        self.running = False

    def update_state(self):
        # Update ball position
        self.ball["x"] += self.ball["dir_x"]
        self.ball["y"] += self.ball["dir_y"]

        # Ball collision with top/bottom walls
        if self.ball["y"] - self.ball["radius"] <= 0 or self.ball["y"] + self.ball["radius"] >= self.height:
            self.ball["dir_y"] *= -1

        # Ball collision with paddles
        for player_id, player in self.players.items():
            if self._check_collision(player):
                # Invert direction of the ball based on the paddle's side
                if player["x"] < self.width // 2:  # Left paddle
                    self.ball["dir_x"] = abs(self.ball["dir_x"])
                else:  # Right paddle
                    self.ball["dir_x"] = -abs(self.ball["dir_x"])

                # adjusts ball speed slightly
                # self.ball["dir_x"] *= 1.1
                # self.ball["dir_y"] *= 1.1

        # Ball out of bounds
        if self.ball["x"] < 0:
            self.score["opponent"] += 1
            self._reset_ball(direction=1)
        elif self.ball["x"] > self.width:
            self.score["player"] += 1
            self._reset_ball(direction=-1)

        if self.score["player"] >= 2 or self.score["opponent"] >= 2:
            winner = "Player" if self.score["player"] >= 2 else "Opponent"
            self.stop_game(winner)

        # Opponent AI movement (only in single-player mode)
        if self.mode == "One Player" and len(self.players) > 1: # or should it be =
            self._move_ai()

    def move_player(self, player_id, direction):
        if self.mode == "Two Players (hot seat)" and player_id in self.players:
            print(f"Moving player {player_id} with direction {direction}", flush=True)
            print("111111")
            #paddle = self.players[player_id]
            player = self.players[player_id]
            opponent = self.players["opponent"]
            if direction == "up" and opponent["y"] > 0:
                opponent["y"] -= 10
            elif direction == "down" and opponent["y"] + opponent["height"] < self.height:
                opponent["y"] += 10
            elif direction == "s_down" and player["y"] + player["height"] < self.height:
                player["y"] += 10
            elif direction == "w_up" and player["y"] > 0:
                player["y"] -= 10

        elif player_id in self.players:
            print(f"Moving player {player_id} with direction {direction}", flush=True)
            print("22222")
            paddle = self.players[player_id]
            if direction == "up" and paddle["y"] > 0:
                paddle["y"] -= 10
                print(f"Player {player_id} moved up to {paddle['y']}", flush=True)
            elif direction == "down" and paddle["y"] + paddle["height"] < self.height:
                paddle["y"] += 10
                print(f"Player {player_id} moved down to {paddle['y']}", flush=True)

    def get_state(self):
        return {
            "players": self.players,
            "ball": self.ball,
            "score": self.score,
            "net": self.net,
            "running": self.running,
            "mode": self.mode,
            "width": self.width,
            "height": self.height
        }

    def _check_collision(self, paddle):
        # predictive collision detection based on ball's direction
        next_x = self.ball["x"] + self.ball["dir_x"]
        next_y = self.ball["y"] + self.ball["dir_y"]

        if (
            next_x + self.ball["radius"] >= paddle["x"]  # Ball will be at or past left edge of paddle
            and next_x - self.ball["radius"] <= paddle["x"] + paddle["width"]  # Ball will be at or before right edge
            and next_y + self.ball["radius"] >= paddle["y"]  # Ball will be at or below top edge of paddle
            and next_y - self.ball["radius"] <= paddle["y"] + paddle["height"]  # Ball will be at or above bottom edge
        ):
            if (self.ball["dir_x"] > 0 and self.ball["x"] < paddle["x"]) or (self.ball["dir_x"] < 0 and self.ball["x"] > paddle["x"] + paddle["width"]):
                return True
            return False

    def _reset_ball(self, direction):
        self.ball["x"] = self.width // 2
        self.ball["y"] = random.randint(200, self.height // 2)
        angle = random.uniform(0.2, 0.8)
        #speed = random.uniform(6, 10) #speed = 8
        speed = math.sqrt(self.ball["dir_x"] ** 2 + self.ball["dir_y"] ** 2)
        
        self.ball["dir_x"] = direction * (speed * 1.2) * angle
        self.ball["dir_y"] = (speed * 1.2) * (1 - angle if random.choice([True, False]) else -1 * (1 - angle))

    def _move_ai(self):
        opponent = None
        for player_id, player in self.players.items():
            if player.get("role") == "opponent":
                opponent = player
                break

        if opponent:
            paddle_center = opponent["y"] + opponent["height"] // 2
            distance_to_ball = self.ball["y"] - paddle_center

            move_step = min(abs(distance_to_ball), 5)
            if distance_to_ball > 0:
                opponent["y"] += move_step
            elif distance_to_ball < 0:
                opponent["y"] -= move_step
            
            # to not go out of bounds
            opponent["y"] = max(0, min(self.height - opponent["height"], opponent["y"]))

    def start_game(self):
        self.running = True

    def stop_game(self, winner):
        self.running = False
        self.players = {}  # Clear players
        self.score = {"player": 0, "opponent": 0}
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4}
        print(f"Game ended. Winner: {winner}", flush=True)