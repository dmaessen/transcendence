# game_logic.py
# Backend logic for handling game state, including ball and paddle movements

import json

class Game:
    def __init__(self, mode):
        self.mode = mode
        self.width = 1400
        self.height = 1000
        self.players = {}  # Use a dictionary to store players by player_id
        self.ball = {"x": self.width // 2, "y": self.height // 2, "radius": 15, "dir_x": 5, "dir_y": 4}
        self.net = {"x": self.width // 2 - 1, "y": 0, "width": 5, "height": 10, "gap": 7}
        self.score = {"player": 0, "opponent": 0}
        self.running = False

    def add_player(self, player_id):
        if player_id not in self.players:
            self.players[player_id] = {"x": 20, "y": self.height // 2 - 50, "width": 20, "height": 100}
            print(f"Player {player_id} added.", flush=True)
            
            if len(self.players) == 1:
                self.players[player_id]["role"] = "player"
            elif len(self.players) == 2:
                self.players[player_id]["role"] = "opponent"
                print(f"Opponent assigned to Player {player_id}", flush=True)

        # Automatically add a bot if only one player (in One Player mode)
        if self.mode == "One Player" and len(self.players) == 1:
            bot_id = "bot"
            self.players[bot_id] = {"x": self.width - 40, "y": self.height // 2 - 50, "width": 20, "height": 100, "role": "opponent"}
            print(f"Bot added as opponent: {bot_id}", flush=True)

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            print(f"Player {player_id} removed.", flush=True)
            if len(self.players) == 0:
                self.running = False  # Stop game if no players are left

    def reset_game(self, mode):
        self.mode = mode
        self.players = {}  # Reset players for a fresh start
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

                # Optionally adjust ball speed slightly (e.g., increase difficulty over time)
                self.ball["dir_x"] *= 1.05
                self.ball["dir_y"] *= 1.05

        # Ball out of bounds
        if self.ball["x"] < 0:
            self.score["opponent"] += 1
            self._reset_ball(direction=1)
        elif self.ball["x"] > self.width:
            self.score["player"] += 1
            self._reset_ball(direction=-1)

        if self.score["player"] >= 10 or self.score["opponent"] >= 10:
            winner = "Player" if self.score["player"] >= 10 else "Opponent"
            self.stop_game(winner)

        # Opponent AI movement (only in single-player mode)
        if self.mode == "One Player" and len(self.players) > 1:
            self._move_ai()

    def move_player(self, player_id, direction):
        if player_id in self.players:
            print(f"Moving player {player_id} with direction {direction}", flush=True)
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
        # Predictive collision detection based on ball's direction
        next_x = self.ball["x"] + self.ball["dir_x"]
        next_y = self.ball["y"] + self.ball["dir_y"]

        return (
            next_x + self.ball["radius"] >= paddle["x"]  # Ball will be at or past left edge of paddle
            and next_x - self.ball["radius"] <= paddle["x"] + paddle["width"]  # Ball will be at or before right edge
            and next_y + self.ball["radius"] >= paddle["y"]  # Ball will be at or below top edge of paddle
            and next_y - self.ball["radius"] <= paddle["y"] + paddle["height"]  # Ball will be at or above bottom edge
        )

    def _reset_ball(self, direction):
        self.ball["x"] = self.width // 2
        self.ball["y"] = self.height // 2
        self.ball["dir_x"] = direction * 4
        self.ball["dir_y"] = 3

    def _move_ai(self):
        opponent = None
        for player_id, player in self.players.items():
            if player.get("role") == "opponent":
                opponent = player
                break

        if opponent:  # Ensure the opponent exists before moving the AI
            if self.ball["y"] < opponent["y"] + opponent["height"] // 2:
                opponent["y"] -= 5
            elif self.ball["y"] > opponent["y"] + opponent["height"] // 2:
                opponent["y"] += 5
            # Prevent the opponent from going out of bounds
            opponent["y"] = max(0, min(self.height - opponent["height"], opponent["y"]))

    def start_game(self):
        self.running = True

    def stop_game(self, winner):
        self.running = False
        print(f"Game ended. Winner: {winner}", flush=True)

# rm this function
# def websocket_game_handler(socket, mode, player_id):
#     try:
#         game = Game(mode)
#         game.add_player(player_id)
#         game.start_game()

#         while game.running:
#             try:
#                 message = socket.receive(timeout=5)  # Add a timeout to prevent indefinite waiting
#                 if message is None:
#                     break

#                 response = handle_message(game, message, player_id)

#                 if response:
#                     socket.send(json.dumps({"type": "update", "data": response}))

#                 if not game.running:
#                     winner = "Player" if game.score["player"] >= 10 else "Opponent"
#                     socket.send(json.dumps({"type": "end", "reason": f"Game Over: {winner} wins"}))
#                     break
#             except TimeoutError:
#                 print("No message received; continuing loop...")
#             except Exception as e:
#                 print(f"Error in WebSocket handler: {e}")
#                 break
#     except Exception as e:
#         print(f"WebSocket connection error: {e}")
#     finally:
#         #game.remove_connection(socket)
#         print("WebSocket connection closed.")
#         socket.close()
