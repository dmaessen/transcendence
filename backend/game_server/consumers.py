import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
#from backend.matchmaking.views import matchmaking

games = {}  # active games by game_id -- laura might need??
players = {}  # active players by player_id -- laura??

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.channel_name
        self.room_name = None # for two players remote
        players[self.player_id] = self
        print(f"Player {self.player_id} connected.", flush=True)

        # Gul? change below to fucntion that pairs/assigns a room
        # self.room_name = await create_a_match(self.player_id)
        # await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()  # accept socket connection

    async def disconnect(self, close_code):
        print(f"Player {self.player_id} disconnected.", flush=True)
        if self.player_id in players:
            del players[self.player_id]
        
        # rm the player from any active games
        for game_id, game in games.items():
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[game_id]

        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.close()
    
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")
        mode = data.get("mode", "One Player")  # default to "One Player" if no mode sent

        if action == "connect":
            game_id = f"game_{self.player_id}"
            if game_id in games:
                game = games[game_id]
                if not game.running:
                    game.reset_game(mode)
            else:
                # Create a new game for this player
                game = Game(mode)
                games[game_id] = game

            if self.player_id not in game.players:
                game.add_player(self.player_id)
            print(f"Game mode set to: {mode}", flush=True)

        elif action == "move":
            direction = data.get("direction")
            if game_id in games:
                game = games[game_id]
                game.move_player(self.player_id, direction)
                await self.send_json({
                    "type": "player_move",
                    "player_id": self.player_id,
                    "direction": direction
                })

        elif action == "reset":
            mode = data.get("mode")
            if game_id in games:
                games[game_id].reset_game(mode)
                await self.send(json.dumps({
                    "type": "reset",
                    "data": games[game_id].get_state(),
                }))
            else:
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Game ID not found for reset.",
                }))
        
        elif action == "start":
            mode = data.get("mode")
            game_id = f"game_{self.player_id}"
            if game_id in games:
                game = games[game_id]
                game.start_game()
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))
                asyncio.create_task(self.broadcast_game_state(game_id))
            else:
                games[game_id] = Game(mode)
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))

        elif action == "stop":
            if game_id in games:
                del games[game_id]
                await self.broadcast_game_state(game_id)
                await self.send(text_data=json.dumps({
                    "type": "end",
                    "reason": "Game stopped by player.",  # change this to something dynamic to see who won
                }))

        elif action == "disconnect":
            del players[self.player_id]
            await self.close()
            print(f"WebSocket disconnected", flush=True)
            await self.channel_layer.group_discard(
                "game_group",
                self.channel_name
            )
        
        #broadcasts the updated game state to the group (for two players remote)
        # await self.channel_layer.group_send(
        #     self.room_name,
        #     {
        #         "type": "update",
        #         "game_id": game_id,
        #         "data": games[game_id].get_state(), #data or game_update
        #     },
        # )

    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]
            while game.running:
                game.update_state()

                await self.send_json({
                    "type": "update",
                    "data": game.get_state()
                })

                if not game.running: 
                    winner = "Player" if game.score["player"] >= 2 else "Opponent"
                    # improve the below with data/name from laura about the player_id
                    await self.send_json({"type": "end", "reason": f"Game Over: {winner} wins"})
                    # socket.close() ???
                    break

                await asyncio.sleep(0.05)

