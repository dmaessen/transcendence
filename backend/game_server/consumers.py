import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from matchmaking.utils import create_match
import uuid

games = {}  # active games by game_id -- laura might need??
players = {}  # active players by player_id -- laura??

#The scope is a set of details about a single incoming connection 
#scope containing the user's username, chosen name, and user ID.

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.player_id = self.scope["user"].id
        else:
            # Use sync_to_async for session creation
            session = await sync_to_async(SessionStore)()
            await sync_to_async(session.create)()
            
            User = get_user_model()
            guest_user = await sync_to_async(User.objects.create)(
                name=f"Guest_{session.session_key}",
                email=f"{session.session_key[:10]}",
                is_active=False
            )
            
            self.player_id = guest_user.id
            self.session_key = session.session_key
        
        await self.accept()
        match_data = await create_match(self.player_id)

        if match_data == "waiting":
            await self.send(text_data=json.dumps({"message": "Waiting for another player..."}))
            self.match_name = f"waiting_room_{self.player_id}"  
            return

        self.match_name = f"match_{match_data['id']}"
        await self.channel_layer.group_add(self.match_name, self.channel_name)

# class GameConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         #while testing in browser, for now we dont have an user in db,
#         #so player_id will be None
#         if self.scope["user"].is_authenticated:
#             self.player_id = self.scope["user"].id
#         else:
#             #if it s not authenticated we can assign scope values manually, 
#             #but then where to store that info?
#             self.player_id = None  # Guest user (will be assigned a negative ID)
        
#         print(f"Player ID: {self.player_id}")
#         await self.accept()  # Accept the WebSocket connection FIRST

#         #self.player_id = self.scope["user"].id  # to ensure this is an integer, i use this in view as int
#         match_data = await create_match(self.player_id)  # ensure this is a valid string

#         #match_data = await create_match(self.player_id)

#         if match_data == "waiting":
#             await self.send(text_data=json.dumps({"message": "Waiting for another player..."}))
#             self.match_name = f"waiting_room_{self.player_id}"  
#             return
#         # if not self.match_name or not isinstance(self.match_name, str):
#         #     self.match_name = f"default_room_{self.player_id}"  # assign a fallback room ??
#         self.match_name = f"match_{match_data['id']}"

#         await self.channel_layer.group_add(self.match_name, self.channel_name)
#         #await self.accept()


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

        if self.match_name:
            await self.channel_layer.group_discard(self.match_name, self.channel_name)
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
        await self.channel_layer.group_send(
            self.match_name,
            {
                "type": "update", #this correct or we want another type?
                "game_id": game_id,
                "data": games[game_id].get_state(), #data or game_update
            },
        )

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

