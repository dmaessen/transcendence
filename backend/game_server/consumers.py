import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game

games = {}  # active games by game_id -- laura??
players = {}  # active players by player_id -- laura??

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #The GameConsumer class uses channel_name to:
        #Assign a unique ID to each player when they connect.
        #self.player_id = self.channel_name if hasattr(self, 'channel_name') else None
        self.player_id = self.channel_name  # unique player ID -- laura??
        players[self.player_id] = self
        print(f"Player {self.player_id} connected.")

        await self.accept() # accepts socket connection

    async def disconnect(self, close_code):
        print(f"Player {self.player_id} disconnected.")
        if self.player_id in players:
            del players[self.player_id]

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")

        if action == "start":
            mode = data.get("mode")
            game_id = f"game_{self.player_id}"
            games[game_id] = Game(mode)
            await self.send(text_data=json.dumps({
                "type": "started",
                "game_id": game_id,
            }))

        elif action == "move":
            direction = data["data"]["direction"]
            if game_id in games:
                game = games[game_id]
                game.move_player(self.player_id, direction)
                await self.broadcast_game_state(game_id)

        elif action == "disconnect":
            del players[self.player_id]
            await self.close()

    #this one channel layer
    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game_state = games[game_id].get_state()
            message = json.dumps({
                "type": "update",
                "data": game_state,
            })
            print(f"Broadcasting game state: {message}")  # Debug log
            for player in players.values():
                await player.send(text_data=message)


