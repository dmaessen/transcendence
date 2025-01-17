import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game

games = {}  # active games by game_id -- laura??
players = {}  # active players by player_id -- laura??

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.channel_name  # Unique player ID
        players[self.player_id] = self
        print(f"Player {self.player_id} connected.")
        
        game_id = f"game_{self.player_id}"
        if game_id in games:
            game = games[game_id]
            if not game.running:  # Reset the game if it's not running
                game.reset_game("One Player")  # Ensure 'mode' is defined
        else:
            # Create a new game for this player
            game = Game("One Player")  # Default mode
            games[game_id] = game

        # Add the player to the game
        game.add_player(self.player_id)
        await self.accept()  # Accept socket connection

# Also adjust the 'disconnect' logic for game removal:
    async def disconnect(self, close_code):
        print(f"Player {self.player_id} disconnected.")
        if self.player_id in players:
            del players[self.player_id]
        
        # Remove the player from any active games
        for game_id, game in games.items():
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[game_id]  # Cleanup only if no players are left
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")

        if action == "reset":
            mode = data.get("mode")
            if game_id in games:
                games[game_id].reset_game(mode)  # Reinitialize the game with the new mode
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
                game.start_game()  # Start the game, if not already started
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))
                asyncio.create_task(self.broadcast_game_state(game_id))  # Broadcast only after starting
            else:
                games[game_id] = Game(mode)
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))
            #mode = data.get("mode")
            #game_id = f"game_{self.player_id}"
            #games[game_id] = Game(mode)
            #await self.send(text_data=json.dumps({
            #    "type": "started",
            #    "game_id": game_id,
            #}))
            #print(f"Game started with ID: {game_id}")  # to rm
            # Start broadcasting game state asynchronously
            #asyncio.create_task(self.broadcast_game_state(game_id))

        elif action == "move":
            direction = data["data"]["direction"]
            if game_id in games:
                game = games[game_id]
                game.move_player(self.player_id, direction)
                await self.broadcast_game_state(game_id)

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

    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]
            while game.running:
                game.update_state()
                game_state = game.get_state()
                message = json.dumps({"type": "update", "data": game_state})
                
                # Broadcast only if game mode is "One Player"
                if game.mode == "One Player":
                    # Gather send operations for all players concurrently
                    send_operations = [
                        player.send(text_data=message) for player in players.values() if player.player_id in game.players
                    ]
                    # Use asyncio.gather to run all send operations concurrently
                    await asyncio.gather(*send_operations)
                
                await asyncio.sleep(0.05)  # Adjust sleep duration as needed
