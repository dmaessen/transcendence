import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import Tournament
from matchmaking.utils import create_match
import uuid

#The scope is a set of details about a single incoming connection 
#scope containing the user's username, chosen name, and user ID.
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

from game_server.player import Player

games = {}  # active games by game_id -- laura might need??
players = {}  # active players by player_id -- laura??
tournament_active = False # for banner popup in frontend
#tournaments = {} #active tournament by id


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
                name=f"Guest_{session.session_key[:12]}",
                email=f"{session.session_key[:10]}",
                is_active=False
            )
            
            self.player_id = guest_user.id
            self.session_key = session.session_key

        player = Player(self.player_id, self.session_key, 'online')
        # self.match_name = None
        # self.match_data = None
        
        await self.accept()


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
    
    async def update(self, event):
        await self.send_json(event["data"])

    async def find_match(self):
        timeout = 300  # 5 minutes max
        start_time = asyncio.get_event_loop().time()

        self.match_name = f"waiting_room_{self.player_id}"  # Unique waiting room
        await self.channel_layer.group_add(self.match_name, self.channel_name)

        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                await self.send(text_data=json.dumps({"message": "Matchmaking timed out."}))
                await self.channel_layer.group_discard(self.match_name, self.channel_name)
                break  # Stop the loop

            self.match_data = await create_match(self.player_id)

            if self.match_data != "waiting":
                # Matched! Move player from waiting room to match group
                await self.channel_layer.group_discard(self.match_name, self.channel_name)
                self.match_name = f"match_{self.match_data['id']}"
                await self.channel_layer.group_add(self.match_name, self.channel_name)

                await self.send(text_data=json.dumps({"message": "Match found!", "match_id": self.match_data['id']}))
                break  # Exit loop

            await self.send(text_data=json.dumps({"message": "Waiting for another player..."}))
            await asyncio.sleep(2)  # Wait before retrying

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")
        mode = data.get("mode", "One Player")  # default to "One Player" if no mode sent
        print("Mode in receive()", mode)

        if action == "connect":
            if mode == "Two Players (remote)":
                asyncio.create_task(self.find_match())
                while self.match_data == "waiting":
                    await asyncio.sleep(1)
                # match_data = await create_match(self.player_id)

                # if match_data == "waiting":
                #     print("Made it here??")
                #     await self.send(text_data=json.dumps({"message": "Waiting for another player..."}))
                #     self.match_name = f"waiting_room_{self.player_id}"
                #     await self.channel_layer.group_add(self.match_name, self.channel_name)
                    
                #     # Wait and try again
                #     await asyncio.sleep(20)  # Adjust the delay as needed
                #     await self.receive(json.dumps({"action": "connect", "mode": mode}))  # Recursively call itself
                #     return

                # self.match_name = f"match_{match_data['id']}"
                # await self.channel_layer.group_add(self.match_name, self.channel_name)

            if mode == "Two Players (remote)":
                game_id = self.match_name
            else:
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
            print(f"Game mode set to: {mode}, with game_id {game_id}", flush=True)

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
        
        # elif action == "waiting":


        elif action == "stop":
            if game_id in games:
                del games[game_id]
                await self.broadcast_game_state(game_id)
                await self.send(text_data=json.dumps({
                    "type": "end",
                    "reason": "Game stopped by player.",  # change this to something dynamic to see who won
                }))

        elif action == "disconnect":
            if self.player_id in players:
                del players[self.player_id]
            await self.close()
            print(f"WebSocket disconnected", flush=True)
            await self.channel_layer.group_discard(
                "game_group",
                self.channel_name
            )

        elif action == "start_tournament":
            tournament_id = f"tournament_{len(tournaments) + 1}"
            tournaments[tournament_id] = {
                "players": [self.player_id],
                "rounds": [],
                "status": "waiting",
                "current_match": None
            }
            await self.send_json({"action": "tournament_status", "active": True, "tournament_id": tournament_id})
            
            global tournament_active
            tournament_active = True
            await self.broadcast_tournament_status(True)

        elif action == "end_tournament": 
            tournament_active = False
            await self.broadcast_tournament_status(False)
        
        #broadcasts the updated game state to the group (for two players remote)
        if game_id in games and self.match_name is not None:
            await self.channel_layer.group_send(
                self.match_name,
                {
                    "type": "update", #this correct or we want another type?
                    # "game_id": game_id,
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

