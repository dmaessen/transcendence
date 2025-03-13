import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import Tournament
from game_server.player import Player
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.core.cache import cache
import uuid
from data.models import CustomUser, Match
import msgspec
import asyncio
from channels.layers import get_channel_layer
from autobahn.websocket.protocol import Disconnected
from datetime import timedelta

games = {}

class TournamentConsumer(AsyncWebsocketConsumer):
    tournament = None  # keeps track of the tournament instance
    initiator = None

    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.player_id = self.scope["user"].id
            self.username = self.scope["user"].username
        else:
            session = await sync_to_async(SessionStore)()
            await sync_to_async(session.create)()
            
            CustomUser = get_user_model()
            unique_username = f"Guest_{uuid.uuid4().hex[:12]}"
            guest_user = await sync_to_async(CustomUser.objects.create)(
                username=unique_username,
                name=f"Guest_{session.session_key[:12]}",
                email=f"{session.session_key[:10]}",
                is_active=False
            )
            print(f"guest user {guest_user.name}")
            
            self.player_id = guest_user.id
            self.session_key = session.session_key
            self.username = guest_user.username

        print(f"player_id == {self.player_id}", flush=True)
        player = Player(self.player_id, self.session_key, 'online')
        
        self.room_name = "tournament_lobby"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print(f"Player connected to tournament WebSocket: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print(f"Player disconnected from tournament WebSocket: {self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "connect":
            await self.handle_connect(data)
        elif action == "start_tournament":
            await self.handle_start_tournament(data)
        elif action == "join_tournament":
            await self.handle_join_tournament(data)
        elif action == "leave_tournament":
            await self.handle_leave_tournament(data)
        # elif action == "match_ready":
        #     await self.handle_match_ready(data)
        elif action == "report_match":
            await self.handle_report_match(data)
        # elif action == "disconnect":
        #     await self.handle_disconnect(data)
        elif action == "game.created":
            await self.game_created(data)
        elif action == "game.result":
            await self.game_result(data)
        elif action == "create.game.tournament":
            await self.create_game_tournament(data)

        elif action == "move":
            direction = data.get("direction")
            if self.game_id in games:
                game = games[self.game_id]
                game.move_player(self.player_id, direction)
                await self.send_json({
                    "type": "player_move",
                    "player_id": self.player_id,
                    "direction": direction
                })
        
        elif action == "start":
            mode = data.get("mode")
            print("STAAAAART 1V1 TOURNAMENT GAME", self.player_id)
            if self.game_id in games:
                game = games[self.game_id]
                game.start_game()
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": self.game_id,
                }))
                asyncio.create_task(self.broadcast_game_state(self.game_id))
            else:
                games[self.game_id] = Game("Two Players (remote)") # as default here
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": self.game_id,
                }))
        
        elif action == "ready":
            if self.game_id in games:
                game = games[self.game_id]
                game.ready_players.add(self.player_id)
                print(f"Player {self.player_id} is ready! Ready count: {len(game.ready_players)}", flush=True)

            if len(game.ready_players) == 2:
                print("Both players are ready. Starting game!", flush=True)
                game.start_game() # this makes them start without having to press on a key
                await self.send_json({"type": "started", "game_id": self.game_id})
                await self.send_game_state(game)
                asyncio.create_task(self.broadcast_game_state(self.game_id))
        
        elif action == "end":
            if self.game_id in games:
                game = games.pop(self.game_id, None)
                if game:
                    game.clear_game()
            else:
                print(f"game has already been cleared {self.game_id}", flush=True)

        elif action == "stop":
            if self.game_id in games:
                del games[self.game_id]
                await self.broadcast_game_state(self.game_id)
                await self.send(text_data=json.dumps({
                    "type": "end",
                    "reason": "Game stopped by player.",  # change this to something dynamic to see who won
                }))

        elif action == "disconnect_1v1game":
            for game_id in list(games.keys()):
                game = games[game_id]
                if self.player_id in game.players:
                    game.remove_player(self.player_id)
                    if not game.players:
                        game.stop_game("No players")
                        del games[game_id]
                        print(f"Game {game_id} ended. Winner: No players", flush=True)
            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)

        elif action == "disconnect": # SEE WHAT WE USE THIS ONE FOR, HAVE ONE FOR THE WHOLE TOURNAMENT WS
            for game_id in list(games.keys()):
                game = games[game_id]
                if self.player_id in game.players:
                    game.remove_player(self.player_id)
                    if not game.players:
                        game.stop_game("No players")
                        del games[game_id]
                        print(f"Game {game_id} ended. Winner: No players", flush=True)

            await self.close() # not sure about this one...
            print(f"WebSocket disconnected for player {self.player_id}", flush=True)

            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)
    
        else:
            print(f"Unknown action: {action}")

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    async def handle_connect(self, data):
        mode = data.get("mode")
        print(f"Player {self.player_id} connected to {mode}-player tournament.")

    async def handle_start_tournament(self, data):
        mode = data.get("mode")
        self.initiator = self.player_id
        self.tournament = Tournament(mode=mode)
        # self.tournament.add_room_name("tournament_lobby")
        print(f"Starting a {mode}-player tournament. Initiator: {self.initiator}")
        await self.broadcast_tournament_state()

    async def handle_join_tournament(self, data):
        tournament_state = cache.get('tournament_state')
        if tournament_state:
            tournament_state = json.loads(tournament_state)
            self.tournament = Tournament(mode=tournament_state['mode'])
            self.tournament.players = tournament_state['players']
        else:
            self.tournament = Tournament(mode=data.get("mode"))

        if len(self.tournament.players) < self.tournament.num_players:
            self.tournament.add_player(self.player_id, self.username)
            print(f"Player {self.player_id} joined the tournament.")
            await self.broadcast_tournament_state()
            if len(self.tournament.players) == self.tournament.num_players:
                print(f"Tournament starting from handle_join_tournament")
                await self.tournament.start_tournament()
                await self.broadcast_tournament_state()
        else:
            await self.tournament_full()
            print(f"Tournament is full. Player {self.player_id} cannot join.")

    async def handle_leave_tournament(self, data): # look more into this one, when applicable
        """Player leaves before the tournament starts."""
        if self.tournament and self.player_id in self.tournament.players:
            self.tournament.players.remove(self.player_id)
            await self.broadcast_tournament_state()
        print(f"Player {self.player_id} left the tournament.")

    # async def handle_match_ready(self, data):
    #     """Acknowledge that the player is ready for their match."""
    #     print(f"Player {self.player_id} is ready for their match.")

    async def handle_report_match(self, data):
        """Report the match result."""
        game_id = data.get("game_id")
        winner = data.get("winner")
        print(f"Game {game_id} finished. Winner: {winner}")

    # async def handle_disconnect(self, data):
    #     """Handle player disconnection."""
    #     print(f"Player {self.player_id} disconnected from tournament.")

    async def tournament_full(self):
        await self.send_json({
            "type": "tournament_full"
        })
    
    async def game_created(self, event):
        game_id = event["game_id"]
        player1 = event["player1"]
        player2 = event["player2"]
        self.tournament.matches.append((player1, player2, game_id))

        print(f"Tournament match {game_id} added: {player1} vs {player2}.", flush=True)
        print(f"Current matches: {self.tournament.matches}", flush=True)
        await self.send_json({
            "type": "match_start",
            # "data": game.get_state()
        })
        await self.broadcast_tournament_state()


    async def game_result(self, event):
        game_id = event["game_id"]
        winner = event["winner"]
        
        if isinstance(winner, str):
            winner_username = winner
        elif isinstance(winner, dict) and "player" in winner:
            winner_username = winner["player"]["username"]
        else:
            print(f"inccorect winner format: {winner}", flush=True)
            return

        # updates the tournament bracket
        self.tournament.register_match_result(game_id, winner_username)
        await self.broadcast_tournament_state()

    async def tournament_update(self, event):
        """Receives the tournament state update and sends it to the frontend"""
        await self.send_json(event["data"])


# NEW FUNCTIONS HERE
    async def send_game_state(self, game):
        game_state = game.get_state()
        game_state_serializable = msgspec.json.encode(game_state).decode("utf-8")

        await self.channel_layer.group_send(
            self.match_name, # this correct???
            {
                "type": "tournament_update",
                "data": game_state_serializable,
            }
        )

    async def create_game_tournament(self, event):
        print("Received tournament creation request:", event, flush=True)

        player1_id = event["player1"]
        player2_id = event["player2"]
        if self.player_id not in [player1_id, player2_id]:
            print(f"Player {self.player_id} is not part of this match. Ignoring message.", flush=True)
            return

        if self.player_id == player1_id:
            user1 = await get_user_by_id(player1_id)
            user2 = await get_user_by_id(player2_id)

            match = await sync_to_async(Match.objects.create)(
                player_1=user1,
                player_2=user2,
                match_time=timedelta(minutes=2)
            )

            # need to: int(self.match_name[6:]) ??? like in connect in consumer.py??
            self.game_id = match.id
            self.match_name = str(f"match_{match.id}")

            await self.channel_layer.group_add(self.match_name, self.channel_name)

            game = Game("Two Players (remote)")
            game.add_player(user1.id, user1.username)
            game.add_player(user2.id, user2.username)
            game.status = "started"
            game.is_partOfTournament()
            # self.tournament.add_match(user1, user2, match.id)
            games[self.game_id] = game

            await self.channel_layer.group_send(
                "tournament_lobby",
                {
                    "type": "game.created",
                    "game_id": self.game_id,
                    "player1": user1.username,
                    "player2": user2.username
                }
            )
            print(f"Game {self.game_id} created for {user1.username} vs {user2.username}.", flush=True)

            await self.send_game_state(game)
            asyncio.create_task(self.broadcast_game_state(self.game_id))
        
        elif self.player_id == player2_id:
            retries = 5
            delay = 5  # 5sec
            for attempt in range(retries):
                try:
                    match = await sync_to_async(Match.objects.get)(player_1_id=player1_id, player_2_id=player2_id)
                    self.game_id = match.id
                    self.match_name = str(f"match_{match.id}")
                    await self.channel_layer.group_add(self.match_name, self.channel_name)

                    game = games.get(match.id)
                    if game:
                        game.status = "started"
                        await self.send_game_state(game)
                        asyncio.create_task(self.broadcast_game_state(self.game_id))
                    else:
                        print(f"Game for match {match.id} not found.", flush=True)
                    break
                except Match.DoesNotExist:
                    print(f"Match not found for player 2 with IDs: {player1_id}, {player2_id}. Retrying {retries - attempt - 1} more times...", flush=True)
                    await asyncio.sleep(delay)
            else:
                print("Failed to retrieve match after several attempts.", flush=True)

            # match = await sync_to_async(Match.objects.filter)(player_2__isnull=True, tournament__isnull=True)
            # match = await sync_to_async(match.first)()
            # await sync_to_async(match.save)()
            # game = games[match.id]
            # self.game_id = match.id
            # self.match_name = str(f"match_{match.id}")
            # await self.channel_layer.group_add(self.match_name, self.channel_name)

        else:
            print(f"Player {self.player_id} is part of this match but will not create the game.", flush=True)

# END NEW FUNCTIONS HERE

    async def broadcast_tournament_state(self):
        if self.tournament:
            # state = self.tournament.get_tournament_state()
            # state["action"] = "update_tournament"
            state = self.tournament.get_tournament_state()

            print(f"(BACKEND) Sending update: {state}", flush=True)

            state_serializable = msgspec.json.encode(state).decode("utf-8")
            cache.set("tournament_state", state_serializable)
            await self.channel_layer.group_send(
                "tournament_lobby", {
                    "type": "tournament_update",
                    "data": state_serializable,
                }
            )

    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]

            while game.running:
                game.update_state()

                await self.send_game_state(game)
                await self.send_json({
                        # "type": "tournament_update",
                        "type": "update",
                        "data": game.get_state()
                    })

                if not game.running:
                    player_username = None
                    opponent_username = None

                    for player_id, player in game.players.items():
                        if player.get("role") == "player":
                            player_username = player.get("username")
                        elif player.get("role") == "opponent":
                            opponent_username = player.get("username")

                    if player_username and opponent_username:
                        winner = player_username if game.score.get("player", 0) >= 3 else opponent_username
                        print(f"Winner determined: {winner}", flush=True)

                        await self.send_json({"type": "end", "reason": f"Game Over: {winner} wins"})
                        await self.channel_layer.group_send(
                            self.match_name,
                            {
                                "type": "end",
                                "reason": f"Game Over: {winner} wins"
                            }
                        )
                        await self.channel_layer.group_send(
                            "tournament_lobby",  # tournament group name
                            {
                                # "action": "game.result",
                                "type": "game.result",
                                "game_id": game_id,
                                "winner": winner
                            }
                        )
                    else:
                        print("Error: Could not determine usernames for winner announcement.", flush=True)
                        print(f"player_username: {player_username}, opponent_username: {opponent_username}", flush=True)
                    break

                await asyncio.sleep(0.05)


async def get_all_matches_count():
    return await sync_to_async(Match.objects.all().count)()

async  def get_user_by_id(user_id):
    return await sync_to_async(CustomUser.objects.get)(id=user_id)

async def get_user_matches(user_id):
    return await sync_to_async(Match.objects.filter)(player_id=user_id)