import json
import random
import math

MAX_BALL_SPEED = 12.0

class Game:
    def __init__(self, mode):
        #self.id = None
        self.mode = mode
        self.width = 1400
        self.height = 1000
        self.players = {}
        self.ready_players = set()
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4, "speed": 4}
        self.bounce_count = 0 # to speed up the ball after x amount of bounces
        self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
        self.score = {"player": 0, "opponent": 0}
        self.running = False
        self.partOfTournament = False
        self.status = None # default can be "waiting", "started"

    def add_player(self, player_id, username, as_player1):
        if player_id not in self.players:
            # if len(self.players) == 0: #first player
            if as_player1 is True: # first player as left paddle
                self.players[player_id] = {"x": 20, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "player", "username": username}
                print(f"Player {player_id} added as Player 1. With username: {username}", flush=True)
            # elif len(self.players) == 1: #second player
            elif as_player1 is False: # second player, right paddle
                self.players[player_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent", "username": username}
                print(f"Player {player_id} added as Player 2 (opponent). With username: {username}", flush=True)
            # else:
            #     print(f"Cannot add more players. Maximum supported is 2.", flush=True)
        
        # automatically add a bot if only one player (in One Player mode)
        if self.mode == "One Player" and len(self.players) == 1:
            bot_id = "bot"
            self.players[bot_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent", "username": "Bot"}
            print(f"Bot added as opponent: {bot_id}. With username: {username}", flush=True)

        if self.mode == "Two Players (hot seat)" and len(self.players) == 1:
            opponent_id = "opponent"
            self.players[opponent_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent", "username": "Opponent"}
            print(f"Opponent added as opponent: {opponent_id}. With username: {username}", flush=True)
    
    def add_player_tournament(self, player_id, username, as_player1):
        if player_id not in self.players:
            if as_player1 is True: # first player on the left
                self.players[player_id] = {"x": 20, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "player", "username": username}
                print(f"Player {player_id} added as Player 1. With username: {username}", flush=True)
            elif as_player1 is False: # second player on the right
                self.players[player_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent", "username": username}
                print(f"Player {player_id} added as Player 2 (opponent). With username: {username}", flush=True)

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            print(f"Player {player_id} removed.", flush=True)
            if len(self.players) == 0:
                self.running = False  # Stop game if no players are left

    def reset_game(self, mode):
        self.mode = mode
        self.players = {}
        self.ready_players.clear()
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4, "speed": 4}
        self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
        self.score = {"player": 0, "opponent": 0}
        self.running = False
        self.partOfTournament = False

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

                # increment bounce, count and check for speed increase
                if self.partOfTournament:
                    self.bounce_count += 1
                    if self.bounce_count % 7 == 0:
                        self._increase_ball_speed()
                else:
                    self.bounce_count += 1
                    if self.bounce_count % 5 == 0:
                        self._increase_ball_speed()

        # Ball out of bounds
        if self.ball["x"] < 0:
            self.score["opponent"] += 1
            self._reset_ball(direction=1)
        elif self.ball["x"] > self.width:
            self.score["player"] += 1
            self._reset_ball(direction=-1)

        if self.partOfTournament == True:
            if self.score["player"] >= 3 or self.score["opponent"] >= 3:
                winner_id = next(
                    (pid for pid, pdata in self.players.items() if self.score[pdata["role"]] >= 3),
                    None
                )
                winner_name = self.players[winner_id]["username"] if winner_id else "Unknown"
                self.stop_game(winner_name)  # Use username instead of "Player" or "Opponent"
        else:
            if self.score["player"] >= 10 or self.score["opponent"] >= 10:
                winner_id = next(
                    (pid for pid, pdata in self.players.items() if self.score[pdata["role"]] >= 10),
                    None
                )
                winner_name = self.players[winner_id]["username"] if winner_id else "Unknown"
                self.stop_game(winner_name)

        # Opponent AI movement (only in single-player mode)
        if self.mode == "One Player" and len(self.players) > 1: # or should it be =
            self._move_ai()

    def move_player(self, player_id, directions):
        if isinstance(directions, str):
            directions = [directions]
        if self.mode == "Two Players (hot seat)" and player_id in self.players:
            player = self.players[player_id]
            opponent = self.players["opponent"]
            for direction in directions:
                if direction == "up" and opponent["y"] > 0:
                    opponent["y"] -= 10
                if direction == "down" and opponent["y"] + opponent["height"] < self.height:
                    opponent["y"] += 10
                if direction == "s_down" and player["y"] + player["height"] < self.height:
                    player["y"] += 10
                if direction == "w_up" and player["y"] > 0:
                    player["y"] -= 10

        elif player_id in self.players:
            paddle = self.players[player_id]
            for direction in directions:
                if direction == "up" and paddle["y"] > 0:
                    paddle["y"] -= 10
                    print(f"Player {player_id} moved up to {paddle['y']}", flush=True)
                if direction == "down" and paddle["y"] + paddle["height"] < self.height:
                    paddle["y"] += 10
                    print(f"Player {player_id} moved down to {paddle['y']}", flush=True)

    def get_state(self):
        return {
            "players": self.players,
            "ready_players": list(self.ready_players),
            "ball": self.ball,
            "score": self.score,
            "net": self.net,
            "running": self.running,
            "mode": self.mode,
            "width": self.width,
            "height": self.height,
            "status": self.status,
            "partOfTournament": self.partOfTournament
        }
    
    def get_state_isrunning(self):
        if self.running == True:
            return True
        else:
            return False

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

    def _increase_ball_speed(self):
        max_speed = 18
        speedup = 1.2

        self.ball["dir_x"] = max(-max_speed, min(max_speed, self.ball["dir_x"] * speedup))
        self.ball["dir_y"] = max(-max_speed, min(max_speed, self.ball["dir_y"] * speedup))

    def _reset_ball(self, direction):
        self.ball["x"] = self.width // 2
        self.ball["y"] = random.randint(200, self.height // 2)
        angle = random.uniform(0.2, 0.8)
        self.ball["speed"] *= 1.2
        self.ball["speed"] = min(self.ball["speed"], MAX_BALL_SPEED) # capping the ball speed to a certain limit
        
        self.ball["dir_x"] = direction * (self.ball["speed"]) * angle
        self.ball["dir_y"] = (self.ball["speed"]) * (1 - angle if random.choice([True, False]) else -1 * (1 - angle))

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
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4, "speed": 4}
        print(f"Game ended. Winner: {winner}", flush=True)
        return {"type": "end", "reason": f"Game Over: {winner} wins", "winner": winner}
        
    def clear_game(self):
        self.players = {}  # Clear players
        self.score = {"player": 0, "opponent": 0}
    
    def is_partOfTournament(self):
        self.partOfTournament = True
