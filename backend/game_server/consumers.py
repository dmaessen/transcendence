import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import TournamentLogic
from matchmaking.utils import create_match
import uuid
import msgspec
from autobahn.websocket.protocol import Disconnected
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
from datetime import timedelta, datetime
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from game_server.player import Player
from data.models import CustomUser, Match
import logging
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

games = {}  # games[game.id] = game ----game is Game()
player_queue = [] # player_id s int

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self, request):
        token = request.COOKIES.get("access_token")
        if token:
            # Validate the JWT token
            access_token = AccessToken(token)
            logger.info(f"----access token: {access_token}\n\n")
            user_id = access_token["user_id"]
            logger.info(f"----userid: {user_id}\n\n")
            # Fetch the user from the database based on the user_id
            try:
                user = await sync_to_async(CustomUser.objects.get)(id=user_id)
                logger.info(f"username: {user.username}")
                self.scope["user"] = user
                logger.info(f"Authenticated user {user.username} connected via WebSocket.")
            except ObjectDoesNotExist:
                logger.warning(f"User with id {user_id} not found.")
                await self.close()
                return
            except Exception as e:
                logger.error(f"Unexpected error while fetching user: {e}")
                await self.close()
                return
        else:
            logger.warning("No token provided.")
            await self.close()  # Close if no token is provided
        #If the user is authenticated, mark them as online
        if self.scope["user"].is_authenticated:
            try:
                user = self.scope["user"]
                logger.info(f"user {user}")
                print(f"user {user}")
                self.player_id = self.scope["user"].id
                self.username = self.scope["user"].username
            except Exception as e:
                logger.exception("Exception during WebSocket connection:")
                await self.close()
                return

        print(f"player_id == {self.player_id}", flush=True)
        print("Before append:", player_queue, flush=True)
        player_queue.append(self.player_id)
        print("After append:", player_queue, flush=True)

        self.room_name = "game_lobby"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        print(f"GameConsumer connected to room: {self.room_name}", flush=True)

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
        if self.player_id in player_queue:
            player_queue.remove(self.player_id)

        for self.game_id, game in games.items():
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[self.game_id]

        user = await get_user_by_id(self.player_id)

        try:
            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)
            elif hasattr(self, 'room_name'):
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
        except Exception as e:
            print(f"Error during disconnection: {e}")
        
        await self.close()
    
    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
    
    async def update(self, event):
        await self.send_json(json.loads(event["data"]))

    async def send_match_data(self, player_id, match_data):
        print(f"Sending match data to Player {player_id}: {match_data}", flush=True)
        await self.send(text_data=json.dumps(match_data))

    async def send_game_state(self, game):
        game_state = game.get_state()
        game_state_serializable = msgspec.json.encode(game_state).decode("utf-8")

        await self.channel_layer.group_send(
            self.match_name,
            {
                "type": "update",
                "data": game_state_serializable,
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Received WebSocket message:", data, flush=True) # to rm
        action = data.get("action")
        #game_id = data.get("game_id")
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
                # await self.send_json({"type": "match_info", "match_name": self.match_name})

                self.game_id = int(self.match_name[6:])
                print("GAME_ID ", self.game_id)

                # asyncio.create_task(self.trigger_start_game_auto_task())

            else:
                # self.game_id = f"game_{player_id}"
                self.game_id = f"game_{str(uuid.uuid4())[:6]}"
                self.match_name = self.game_id
                await self.send(text_data=json.dumps({
                    'action': 'created',
                    'gameId': self.game_id #in old version it was "'gameId': self.player_id" but it didnt make sense now,
                                            # so i made it 'gameId': self.game_id, lmk if that breaks anything
                }))

                #  THIS COMMENT-OUT VERSION WAS THE REASON OF "KEY ERROR"
                # match = await sync_to_async(Match.objects.create)(
                #     player_1=user, 
                #     match_time=timedelta(minutes=2)
                # )
                # self.match_name = self.game_id
                # await self.send(text_data=json.dumps({
                #     'action': 'created',
                #     'gameId': match.id
                # }))
                if self.game_id in games:
                    game = games[self.game_id]
                    # if not game.running:
                    #     game.reset_game(mode)
                else:
                    game = Game(mode)
                    games[self.game_id] = game

                if self.player_id not in game.players:
                    game.add_player(player_id, self.username, as_player1=True)
            print(f"Game mode set to: {mode}, with game_id {self.game_id}", flush=True)
            game = games[self.game_id]

            if len(game.players) == 2 and mode != "One Player" and mode != "Two players (hot seat)": #start game if two players connected  and mode == "Two Players (remote)"
                    #game.start_game() # this makes them start without having to press on a key
                    #await self.send_json({"type": "started", "game_id": self.game_id})
                    asyncio.create_task(self.trigger_start_game_auto_task())
                    await self.send_game_state(game)
                    asyncio.create_task(self.broadcast_game_state(self.game_id))
    
        elif action == "move":
            direction = data.get("direction")
            print("MOVEEEE ", player_id)
            if self.game_id in games:
                game = games[self.game_id]
                game.move_player(player_id, direction)
                await self.send_json({
                    "type": "player_move",
                    "player_id": player_id,
                    "direction": direction
                })

        elif action == "reset":
            mode = data.get("mode")
            if self.game_id in games:
                games[self.game_id].reset_game(mode)
                await self.send(json.dumps({
                    "type": "reset",
                    "data": games[self.game_id].get_state(),
                }))
            else:
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Game ID not found for reset.",
                }))
        
        elif action == "start":
            mode = data.get("mode")
            print("STAAAAART ", player_id)
            #self.game_id = f"game_{player_id}"
            if self.game_id in games:
                game = games[self.game_id]
                game.start_game()
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": self.game_id,
                }))
                asyncio.create_task(self.broadcast_game_state(self.game_id))
            else:
                games[self.game_id] = Game(mode)
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": self.game_id,
                }))
        
        elif action == "ready":
            if self.game_id in games:
                game = games[self.game_id]
                game.ready_players.add(player_id)
                print(f"Player {player_id} is ready! Ready count: {len(game.ready_players)}", flush=True)

            if mode == "Two Players (remote)" or mode == "4" or mode == "8":
                if len(game.ready_players) == 2:
                    print("Both players are ready. Starting game!", flush=True)
                    game.start_game() # this makes them start without having to press on a key
                    await self.send_json({"type": "started", "game_id": self.game_id})
                    await self.send_game_state(game)
                    asyncio.create_task(self.broadcast_game_state(self.game_id))
                    # game.ready_players.clear()

        elif action == "stop":
            if self.game_id in games:
                del games[self.game_id]
                await self.broadcast_game_state(self.game_id)
                reason = _("Game stopped by player.")
                await self.send(text_data=json.dumps({
                    "type": "end",
                    "reason": reason,
                }))

        elif action == "disconnect":
            for game_id in list(games.keys()):
                game = games[game_id]
                if self.player_id in game.players:
                    game.remove_player(self.player_id)
                    # if not game.players or if len(game.players) is 1 and game.mode is "Two Players (hot seat)" or "One Player":
                    if (
                        not game.players or
                        (len(game.players) == 1 and game.mode in ["Two Players (hot seat)", "One Player"])
                    ):
                        game.stop_game("No players")
                        del games[game_id]
                        print(f"Game {game_id} ended. Winner: No players", flush=True)

            await self.close()
            print(f"WebSocket disconnected for player {self.player_id}", flush=True)

            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)

    async def find_match(self, user):
        print(f"Player {self.player_id} entered find_match()", flush=True)
        match = await sync_to_async(Match.objects.filter)(player_2__isnull=True, tournament__isnull=True)
        if await sync_to_async(match.count)() == 0:
            await self.create_game(self.player_id)
            match = await sync_to_async(Match.objects.latest)('id')
        else:
            match = await sync_to_async(match.first)()
            self.match_name = await self.join_game(match, 2, self.player_id)

        player_queue.remove(self.player_id)

    async def create_game(self, player_id):
        print(f"Player {self.player_id} entered create_game()", flush=True)
        user = await get_user_by_id(player_id)
        #game = await sync_to_async(Match.objects.create)(player_1=user) #single player in game
        # date_match = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        date_match = datetime.now()

        match = await sync_to_async(Match.objects.create)(
            player_1=user,
            match_start = date_match,
            match_time = timedelta(minutes=0),
        )
        await self.send(text_data=json.dumps({
            'action': 'created',
            'gameId': match.id
        }))

        game = Game("Two Players (remote)")
        #game.add_player(player_id)
        #adding a game to games dict. game by gameid
        games[match.id] = game
        print("MATCH.ID ", match.id)
        # self.match_name = str(f"match_{match.id}")
        # await self.channel_layer.group_add(self.match_name, self.channel_name)
        await self.join_game(match, 1, player_id)

    async def join_game(self, match, numb_of_players, player_id):
        print(f"Player {self.player_id} entered join_game()", flush=True)
        user = await get_user_by_id(player_id)
        if numb_of_players == 1:
            game = games[match.id]
            #game.players[user.id] = user
            game.add_player(user.id, self.username, as_player1=True)
            game.status = "waiting"
        else:
            match.player_2 = user
            #self.match_name = str(f"match_{match.id}")
            await sync_to_async(match.save)()
            print(f"Available games: {list(games.keys())}", flush=True)
            print(f"Trying to access game for match.id={match.id}", flush=True)
            game = games[match.id] #this game represents Game(), not Match model
            #game.players[user.id] = user
            game.add_player(user.id, self.username, as_player1=False)
            game.status = "started"
            #self.match_name = str(f"match_{match.id}")
            #await self.channel_layer.group_add(self.match_name, self.channel_name)
            #await self.send_game_state(game)

            # asyncio.create_task(self.trigger_start_game_auto_task(match.id))

        self.match_name = str(f"match_{match.id}")
        await self.channel_layer.group_add(self.match_name, self.channel_name)
        #await self.send_game_state(game)

        return self.match_name
    
    async def end(self, event):
        if self.game_id in games:
            game = games[self.game_id]
            try:
                match = await sync_to_async(
                    lambda: Match.objects.select_related("player_1", "player_2").get(id=self.game_id)
                )()
                logger.info(f"Match id: {match.id}, players: {match.player_1.username} vs {match.player_2.username}")
                if match.player_1.username == event.get("winner"):
                    match.winner = match.player_1
                    match.player_1_points = 10
                    match.player_2_points = game.score["opponent"]
                elif match.player_2.username == event.get("winner"):
                    match.winner = match.player_2
                    match.player_2_points = 10
                    match.player_1_points = game.score["player"]
                else:
                    raise ValueError(f"Winner username not found in match")
                await sync_to_async(match.save)()
                logger.info("Match saved successfully")
            except Exception as e:
                logger.error(f"Error processing game result: {e}")

            game.clear_game()

    async def end_twoplayers(self, winner_username):
        if self.game_id in games:
            game = games[self.game_id]
            try:
                match = await sync_to_async(
                    lambda: Match.objects.select_related("player_1", "player_2").get(id=self.game_id)
                )()
                logger.info(f"Match id: {match.id}, players: {match.player_1.username} vs {match.player_2.username}")
                if match.player_1.username == winner_username:
                    match.winner = match.player_1
                    match.player_1_points = game.score["player"]
                    match.player_2_points = game.score["opponent"]
                elif match.player_2.username == winner_username:
                    match.winner = match.player_2
                    match.player_2_points = game.score["opponent"]
                    match.player_1_points = game.score["player"]
                else:
                    raise ValueError(f"Winner username not found in match")
                await sync_to_async(match.save)()
                logger.info("Match saved successfully")
            except Exception as e:
                logger.error(f"Error processing game result: {e}")

            game.clear_game()

    async def trigger_start_game_auto_task(self, duration=70):
        print(f"Game {self.game_id} in trigger_start_game_auto_task", flush=True)
        await asyncio.sleep(duration)  # 1min 10sec wait
        if self.game_id in games:
            game = games[self.game_id]

            if game.get_state_isrunning() == False:
                print("Both players aren't responding, starting game regardless. Starting game!", flush=True)
                await self.send_json({"type": "trigger_auto_start", "game_id": self.game_id})
                print(f"LEN PLAYERS ", len(game.players), len(game.ready_players), flush=True)

                # if someone desconnected in the meantime before starting then this player wins automatically
                await asyncio.sleep(10)
                if len(game.players) == 1:
                    print(f"NB2: Both players aren't responding, starting game regardless. Starting game!", flush=True)
                    reason = _("Game Over: %(winner)s wins") % {'winner': self.username}
                    await self.send_json({"type": "end", "reason": reason, "winner": self.username})
    
    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]
            points = 3 if game.mode in ["4", "8"] else 10

            while game.running:
                game.update_state()

                await self.send_game_state(game)
                await self.send_json({
                        "type": "update",
                        "data": game.get_state()
                    })

                if len(game.players) == 1 and game.mode == "Two Players (remote)":
                    # meaning someone just disconnected/exited
                    if self.player_id in game.players:
                        game.remove_player(self.player_id)
                        if not game.players: # meaning this player was the last one standing
                            game.stop_game({self.username})
                            del games[self.game_id]

                    print(f"Winner determined by default (due to disconnection): {self.username}", flush=True)
                    reason = _("Game Over: %(winner)s wins") % {'winner': self.username}
                    await self.send_json({"type": "end", "reason": reason, "winner": self.username})
                    await self.end_twoplayers({self.username})
                    break

                if not game.running:
                    player_username = None
                    opponent_username = None

                    for player_id, player in game.players.items():
                        if player.get("role") == "player":
                            player_username = player.get("username")
                        elif player.get("role") == "opponent":
                            opponent_username = player.get("username")

                    if player_username and opponent_username:
                        winner = player_username if game.score.get("player", 0) >= points else opponent_username
                        print(f"Winner determined: {winner}", flush=True)

                        reason = _("Game Over: %(winner)s wins") % {'winner': winner}
                        await self.send_json({"type": "end", "reason": reason, "winner": winner})

                        await self.channel_layer.group_send(
                            self.match_name,
                            {
                                "type": "end",
                                "reason": reason,
                                "winner": winner
                            }
                        )
                    else:
                        print("Error: Could not determine usernames for winner announcement.", flush=True)
                        print(f"player_username: {player_username}, opponent_username: {opponent_username}", flush=True)
                    break

                await asyncio.sleep(0.05)

#TODO this functions exist on data 
async def get_all_matches_count():
    return await sync_to_async(Match.objects.all().count)()

async  def get_user_by_id(user_id):
    return await sync_to_async(CustomUser.objects.get)(id=user_id)

async def get_user_matches(user_id):
    return await sync_to_async(Match.objects.filter)(player_id=user_id)