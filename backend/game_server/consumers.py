import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import Tournament
from matchmaking.utils import create_match
import uuid
import msgspec

from datetime import timedelta

#The scope is a set of details about a single incoming connection 
#scope containing the user's username, chosen name, and user ID.
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
#from data.services import get_all_matches_count, get_user_by_id

from game_server.player import Player
from data.models import CustomUser, Match

games = {}  # games[game.id] = game ----game is Game()
#player_queue = {} # self.player_queue[user.id] = f"{game.id}"
player_queue = [] #player_id s int

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.player_id = self.scope["user"].id
        else:
            # Use sync_to_async for session creation
            session = await sync_to_async(SessionStore)()
            await sync_to_async(session.create)()
            
            CustomUser = get_user_model()
            unique_username = f"Guest_{uuid.uuid4().hex[:12]}"  # Generate a unique username
            guest_user = await sync_to_async(CustomUser.objects.create)(
                username=unique_username,  # Set the unique username
                name=f"Guest_{session.session_key[:12]}",
                email=f"{session.session_key[:10]}",
                is_active=False
            )
            print(f"guest user {guest_user.name}")
            
            self.player_id = guest_user.id
            self.session_key = session.session_key

        print(f"player_id == {self.player_id}", flush=True)
        player = Player(self.player_id, self.session_key, 'online')
        player_queue.append(self.player_id)
        #self.match_data = "waiting"
        
        await self.accept()

    async def check_connection_timeout(self):
        await asyncio.sleep(30)  # 30-second timeout
        if not hasattr(self, 'match_name') or not self.match_name:
            await self.send(text_data=json.dumps({
                "type": "connection_timeout",
                "message": "Connection timed out"
            }))
            await self.close()

    async def disconnect(self, close_code):
        print(f"Player {self.player_id} disconnected unexpectedly. Close code: {close_code}", flush=True)

        print(f"Player {self.player_id} disconnected.", flush=True)

        for game_id, game in games.items():
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[game_id]

        user = await get_user_by_id(self.player_id)


        try:
            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)
        except Exception as e:
            print(f"Error during disconnection: {e}")
        
        await self.close()
    
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
    
    async def update(self, event):
        await self.send_json(event["data"])

    async def send_match_data(self, player_id, match_data):
        print(f"Sending match data to Player {player_id}: {match_data}", flush=True)
        await self.send(text_data=json.dumps(match_data))

    async def send_game_state(self, game):
        game_state = game.get_state()
        # game_state_str_keys = {
        #     str(k): v if not isinstance(v, dict) else {str(inner_k): inner_v for inner_k, inner_v in v.items()}
        #     for k, v in game_state.items()
        # }
        #game_state_serializable = msgspec.json.encode(game_state).decode("utf-8")  # Ensures proper JSON formatting
        game_state_serializable = msgspec.json.encode(game_state).decode("utf-8")

        await self.channel_layer.group_send(
            self.match_name,
            {
                "type": "update",
                "data": game_state_serializable,
            }
        )
        print(f"out of send_game_sate {self.player_id}", flush=True)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")
        mode = data.get("mode", "One Player")
        player_id = self.player_id
        user = await get_user_by_id(player_id)

        if action == "connect":
            print(f"Player {player_id} trying to connect to game.", flush=True)
            if mode == "Two Players (remote)":
                await self.find_match(player_id)
                print(f"Player {self.player_id} finished matchmaking, match_name: {self.match_name}", flush=True)
                if self.match_name is None:
                    print(f"ERROR: Player {player_id} failed matchmaking, re-entering queue!", flush=True)
                    await self.send(text_data=json.dumps({"error": "Matchmaking failed"}))
                    return
                await self.send_json({"type": "match_info", "match_name": self.match_name}) #new

                game_id = int(self.match_name[6:])
                print("GAME_ID ", game_id)

            else:
                game_id = f"game_{player_id}"

                if game_id in games:
                    game = games[game_id]
                    # if not game.running:
                    #     game.reset_game(mode)
                else:
                    game = Game(mode)
                    games[game_id] = game

                if self.player_id not in game.players:
                    game.add_player(player_id)
            print(f"Game mode set to: {mode}, with game_id {game_id}", flush=True)
            game = games[game_id]

            if game_id in games:
                print("LAAAAAAA")
            if len(game.players) == 2: #start game if two players connected
                    game.start_game()
                    await self.send_json({"type": "started", "game_id": game_id})
                    await self.send_game_state(game)
                    asyncio.create_task(self.broadcast_game_state(game_id))

        elif action == "move":
            direction = data.get("direction")
            print("KOOOO")
            if game_id in games:
                game = games[game_id]
                game.move_player(player_id, direction)
                await self.send_json({
                    "type": "player_move",
                    "player_id": player_id,
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
            game_id = f"game_{player_id}"
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
            # if player_id in players:
            #     del players[player_id]
            await self.close()
            print(f"WebSocket disconnected", flush=True)
            await self.channel_layer.group_discard(
                "game_group",
                self.channel_name
            )
        
        #broadcasts the updated game state to the group (for two players remote)
        if game_id in games and mode == "Two Players (remote)": # or tournament??
            game = games[game_id]
            #await self.send_game_state(game)

            # await self.channel_layer.group_send(
            #     self.match_name,
            #     {
            #         "type": "update", #this correct or we want another type?
            #         # "game_id": game_id,
            #         "data": games[game_id].get_state(), #data or game_update
            #     },
            # )

    async def find_match(self, user):
        print(f"Player {self.player_id} entered find_match()", flush=True)
        # timeout = 300  # 5 min max
        # start_time = asyncio.get_event_loop().time()

        #self.match_name = f"waiting_room_{player_id}"
        #await self.channel_layer.group_add(self.match_name, self.channel_name)

        match = await sync_to_async(Match.objects.filter)(player_2__isnull=True, tournament__isnull=True)
        if await sync_to_async(match.count)() == 0:
            await self.create_game(self.player_id)
        else:
            match = await sync_to_async(match.first)()
            self.match_name = await self.join_game(match, 2, self.player_id)

        player_queue.remove(self.player_id)
        #player_queue[user.id] = f"{game.id}"
        #return self.match_name
        # while True:
        #     # if asyncio.get_event_loop().time() - start_time > timeout:
        #     #     await self.send(text_data=json.dumps({"message": "Matchmaking timed out."}))
        #     #     print(f"Matchmaking timed out.", flush=True)
        #     #     await self.channel_layer.group_discard(self.match_name, self.channel_name)
        #     #     break
        #     self.match_data = await create_match(self, self.player_id)
        #     print(f"Player {self.player_id} received match_data: {self.match_data}", flush=True)

        #     # if self.match_data == "waiting":
        #     #     await asyncio.sleep(5)
        #     #     continue

        #     if isinstance(self.match_data, dict) and 'id' in self.match_data:
        #         match_id = self.match_data['id']
        #         # self.match_data = {str(k): v for k, v in self.match_data.items()}
        #         self.match_name = str(f"match_{match_id}")
        #         print(f"Player {self.player_id} assigned match_name: {self.match_name}", flush=True)

        #         await self.channel_layer.group_add(self.match_name, self.channel_name)

        #         print(f"Match found: {match_id} with player IDs {self.match_data['player_1']} and {self.match_data['player_2']}", flush=True)

        #         game = Game("Two Players (remote)")
        #         games[self.match_name] = game
        #         game.add_player(self.match_data['player_1'])
        #         game.add_player(self.match_data['player_2'])

        #         await self.send_json({
        #             "type": "match_found",
        #             "game_id": match_id,
        #             "player_1": self.match_data['player_1'],
        #             "player_2": self.match_data['player_2']
        #         })

        #         print(f"Sending match update: {self.match_name} -> {game.get_state()}", flush=True)

        #         await self.send_game_state(game)
        #         print(f"Breaking loop for Player {self.player_id}, match_name: {self.match_name}", flush=True)
        #         break

        #     print(f"Invalid match data received: {self.match_data}", flush=True)
        #     await asyncio.sleep(5)

    async def create_game(self, player_id):
        print(f"Player {self.player_id} entered create_game()", flush=True)
        user = await get_user_by_id(player_id)
        #game = await sync_to_async(Match.objects.create)(player_1=user) #single player in game
        
        match = await sync_to_async(Match.objects.create)(
            player_1=user, 
            match_time=timedelta(minutes=2)
        )
        await self.send(text_data=json.dumps({
            'action': 'created',
            'gameId': match.id
        }))
        game = Game("Two Players (remote)")
        game.add_player(player_id)
        #game.players[user.id] = user
        #adding a game to games dict. game by gameid
        games[match.id] = game
        print("MATCH.ID ", match.id)
        self.match_name = str(f"match_{match.id}")
        await self.channel_layer.group_add(self.match_name, self.channel_name)
        
        #join_game with 1 player??? (game, 1, user)
        await self.join_game(match, 1, player_id)

    async def join_game(self, match, numb_of_players, player_id):
        user = await get_user_by_id(player_id)
        if numb_of_players == 1:
            game = games[match.id]
            #game.players[user.id] = user
            game.add_player(user.id)
            game.status = "waiting"
        else:
            match.player_2 = user
            self.match_name = str(f"match_{match.id}")
            await sync_to_async(match.save)()
            game = games[match.id] #this game represents Game(), not Match model
            #game.players[user.id] = user
            game.add_player(user.id)
            game.status = "started"
            self.match_name = str(f"match_{match.id}")
            await self.channel_layer.group_add(self.match_name, self.channel_name)
        
        #await self.send_game_state(game)

        return self.match_name


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
    
async def get_all_matches_count():
    return await sync_to_async(Match.objects.all().count)()

async  def get_user_by_id(user_id):
    return await sync_to_async(CustomUser.objects.get)(id=user_id)

async def get_user_matches(user_id):
    return await sync_to_async(Match.objects.filter)(player_id=user_id)