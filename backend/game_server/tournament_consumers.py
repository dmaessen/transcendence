import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import TournamentLogic
from game_server.player import Player
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.core.cache import cache
import uuid
from data.models import CustomUser, Match, Tournament
import msgspec
import asyncio
from channels.layers import get_channel_layer
from autobahn.websocket.protocol import Disconnected
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)
games = {}

class TournamentConsumer(AsyncWebsocketConsumer):
    tournament = None  # keeps track of the tournament instance
    initiator = None

    async def connect(self):
        # Retrieve the token from the cookies
        cookies = self.scope.get("headers", [])
        token = None
        for header in cookies:
            if header[0].decode("utf-8") == "cookie":
                cookie_header = header[1].decode("utf-8")
                cookies_dict = {k.strip(): v.strip() for k, v in (cookie.split("=") for cookie in cookie_header.split(";"))}
                token = cookies_dict.get("access_token")
                break

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
        
        self.room_name = "tournament_lobby"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print(f"Player connected to tournament WebSocket: {self.channel_name}")

    async def disconnect(self, close_code):
        print(f"Player disconnected from tournament WebSocket: {self.channel_name}", flush=True)

        if hasattr(self, 'match_name'):
            await self.channel_layer.group_discard(self.match_name, self.channel_name)
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

        if self.tournament and not self.tournament.running and self.player_id in self.tournament.players:
            self.tournament.players.remove(self.player_id)
            await self.broadcast_tournament_state()

        # Final cleanup if this was the last player and the tournament is over
        if self.tournament and not self.tournament.running and self.tournament.final_winner is not None:
            if self.initiator == self.scope["user"]:
                TournamentConsumer.tournament = None
                TournamentConsumer.initiator = None

            await self.send_json({"type": "end_tournament"})

            # Reset tournament cache
            state = default_tournament_state.copy()
            state_serializable = msgspec.json.encode(state).decode("utf-8")
            cache.delete("tournament_state")
            cache.set("tournament_state", state_serializable)

        print(f"WebSocket fully disconnected", flush=True)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "connect":
            await self.handle_connect(data)
        elif action == "start_tournament":
            await self.handle_start_tournament(data)
        elif action == "join_tournament":
            await self.handle_join_tournament(data)
        elif action == "game.created":
            await self.game_created(data)
        elif action == "game.result":
            await self.game_result(data)
        elif action == "game.end":
            await self.game_end(data)
        elif action == "create.game.tournament":
            await self.create_game_tournament(data)
        elif action == "tournament.winners":
            await self.tournament_winners(data)
        # elif action == "tournament.timeout":
        #     await self.tournament_timeout(data)
        elif action == "force.cache.update":
            await self.force_cache_update(data)

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

                # if timer done then this player is winner, game ends
                if len(game.ready_players) == 1:
                    asyncio.create_task(self.tournament1v1game_timeout_task(self.game_id, self.player_id))

                if len(game.ready_players) == 2:
                    print("Both players are ready. Starting game!", flush=True)
                    game.start_game()
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

        # elif action == "disconnect_1v1game":
        #     for game_id in list(games.keys()):
        #         game = games[game_id]
        #         print(f"Game {game_id} ended, in disconnect_1v1game", flush=True)
        #         if self.player_id in game.players:
        #             game.remove_player(self.player_id)
        #             if not game.players:
        #                 game.stop_game("No players")
        #                 del games[game_id]
        #                 print(f"Game {game_id} ended. Winner: No players", flush=True)
        #         if hasattr(self, 'match_name'):
        #             await self.channel_layer.group_discard(self.match_name, self.channel_name)

        elif action == "disconnect_1v1game":
            game_id = data.get("game_id")
            if game_id is None or game_id not in games:
                print(f"Invalid or unknown game_id in disconnect_1v1game", flush=True)
                return

            game = games[game_id]
            print(f"Game {game_id} ended, in disconnect_1v1game", flush=True)

            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[game_id]
                    print(f"Game {game_id} ended. Winner: No players", flush=True)

            if hasattr(self, 'match_name'):
                await self.channel_layer.group_discard(self.match_name, self.channel_name)

        elif action == "disconnect":
            await self.handle_player_leave()
            await self.close()
    
        else:
            print(f"Unknown action: {action}")

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    async def handle_connect(self, data):
        mode = data.get("mode")
        print(f"Player {self.player_id} connected to {mode}-player tournament.")

    async def handle_start_tournament(self, data):
        if self.tournament and self.tournament.running:
            logger.warning("Tournament already running. Cannot start a new one.")
            return

        mode = data.get("mode")
        self.initiator = self.player_id
        self.tournament = TournamentLogic(mode=mode)
        print(f"Starting a {mode}-player tournament. Initiator: {self.initiator}", flush=True)

        tournament_obj = await sync_to_async(Tournament.objects.create)(
            max_players=mode,
            start_date=timezone.now() + timedelta(minutes=2),
        )
        self.tournament_db_id = tournament_obj.id
        print(f"Created tournament with ID {tournament_obj.id} in database", flush=True)

        await self.send_json({
            "type": "join_tournament",
        })

        await self.broadcast_tournament_state()

    async def handle_join_tournament(self, data):
        raw = cache.get('tournament_state')
        if raw:
            tournament_state = msgspec.json.decode(raw.encode("utf-8"))
            self.tournament = TournamentLogic(mode=tournament_state['mode'])
            self.tournament.players = tournament_state['players']
            self.tournament.winners = tournament_state.get("winners", [])
            self.tournament.current_round = tournament_state.get("current_round", 1)

            # Get the tournament_db id from cache if exists
            if 'tournament_db_id' in tournament_state:
                self.tournament_db_id = tournament_state['tournament_db_id']
        else:
            self.tournament = TournamentLogic(mode=data.get("mode"))

        if len(self.tournament.players) < self.tournament.num_players:
            if self.player_id not in [p["id"] for p in self.tournament.players]:
                self.tournament.add_player(self.player_id, self.username)
                pID = self.player_id
                tID = self.tournament_db_id
                user = await sync_to_async(CustomUser.objects.get)(id=pID)
                atournament = await sync_to_async(Tournament.objects.get)(id=tID)
                await sync_to_async(user.tournaments.add)(atournament)
                print(f"Player {self.player_id} joined the tournament.")
            else:
                print(f"Player {self.player_id} ALREADY in the tournament.")
                return
        else:
            await self.tournament_full()
            print(f"Tournament is full. Player {self.player_id} cannot join.")
            return

        state = self.tournament.get_tournament_state()
        if hasattr(self, 'tournament_db_id'):
            state['tournament_db_id'] = self.tournament_db_id

        state_serializable = msgspec.json.encode(state).decode("utf-8")
        cache.delete("tournament_state")
        cache.set("tournament_state", state_serializable)

        await self.broadcast_tournament_state()

        if len(self.tournament.players) == self.tournament.num_players:
            print(f"Tournament starting from handle_join_tournament")
            await self.tournament.start_tournament()
            await self.send_json({
                "type": "ongoing_tournament",
            })
            await self.broadcast_tournament_state()
            
    async def tournament_full(self):
        await self.send_json({
            "type": "tournament_full"
        })

    async def tournament_timeout(self, event):
        print(f"Tournament cancelled for {self.player_id}", flush=True)
        if self.tournament:
            if any(player["id"] == self.player_id for player in self.tournament.players):
                matches = event["unresolved_matches"]
                if matches:
                    if self.game_id in games:
                        game = games[self.game_id]
                        if self.player_id in game.players:
                            game.remove_player(self.player_id)
                            if not game.players:
                                game.stop_game("No players")
                                del games[self.game_id]
                                print(f"Game {self.game_id} ended. Winner: No players", flush=True)

                await self.broadcast_tournament_state()

                self.tournament.running = False
                self.tournament.final_winner = None # should we add random name just for frontend to reset properly??
                TournamentConsumer.tournament = None
                TournamentConsumer.initiator = None

                await self.send_json({"type": "end_tournament"})

                # Optionally reset state in cache
                state = default_tournament_state.copy()
                state_serializable = msgspec.json.encode(state).decode("utf-8")
                cache.delete("tournament_state")
                cache.set("tournament_state", state_serializable)

    async def handle_player_leave(self):
        if self.tournament and not self.tournament.running:
            if self.player_id in self.tournament.players:
                self.tournament.players.remove(self.player_id)
                await self.broadcast_tournament_state()

        game_id = getattr(self, "game_id", None)
        # if self.game_id in games:
        if game_id and game_id in games:
            game = games[self.game_id]
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[self.game_id]
                    print(f"Game {self.game_id} ended. Winner: No players", flush=True)
                else:
                    # Declare remaining player as winner
                    for player_id, player in game.players.items():
                        winner = player.get("username")
                        if winner:
                            print(f"Winner determined: {winner}", flush=True)
                            game.stop_game(winner)
                            game.reset_game("Two Players (remote)") 
                            reason = reason = _("Game Over: %(winner)s wins") % {'winner': winner}
                            await self.channel_layer.group_send(
                                self.match_name,
                                {"type": "game.end", "reason": reason}
                                # {"type": "game.end", "reason": f"Game Over: {winner} wins"}
                            )
                            await self.channel_layer.group_send(
                                "tournament_lobby",
                                {"type": "game.result", "game_id": self.game_id, "winner": winner}
                            )
                            break
    
    async def tournament1v1game_timeout_task(self, game_id, player_id, duration=30):
        print(f"Game {game_id} in tournament1v1game_timeout_task", flush=True)
        await asyncio.sleep(duration)  # 30sec
        if game_id in games:
            game = games[game_id]
            if game.get_state_isrunning() == False:
                print(f"Game {game_id} in tournament timed out. Declaring a winner {player_id}.", flush=True)
                if self.username:
                    winner = self.username
                    print(f"Winner determined: {winner}", flush=True)

                    await self.send_json({"type": "end", "reason": f"Game Over: {winner} wins", "winner": winner})
                    reason = reason = _("Game Over: %(winner)s wins") % {'winner': winner}
                    await self.channel_layer.group_send(
                        self.match_name,
                        {
                            "type": "game.end",
                            "reason": reason
                            # "reason": f"Game Over: {winner} wins"
                        }
                    )
                    await self.channel_layer.group_send(
                        "tournament_lobby",
                        {
                            "type": "game.result",
                            "game_id": game_id,
                            "winner": winner
                        }
                    )
    
    async def tournament1v1game_start_game_task(self, game_id, duration=70):
        print(f"Game {game_id} in tournament1v1game_start_game_task", flush=True)
        await asyncio.sleep(duration)  # 1min 10sec wait
        if self.game_id in games:
            game = games[self.game_id]

            if game.get_state_isrunning() == False:
                print("Both players aren't responding, starting game regardless. Starting game!", flush=True)
                await self.send_json({"type": "trigger_auto_start", "game_id": self.game_id})
                print(f"LEN PLAYERS ", len(game.players), len(game.ready_players), flush=True)

                # if someone desconnected in the meantime before starting then this player wins automatically
                await asyncio.sleep(10)
                # if len(game.players) == 1:
                #     print(f"NB2: Both players aren't responding, starting game regardless. Starting game!", flush=True)
                #     reason = reason = _("Game Over: %(winner)s wins") % {'winner': self.username}
                #     await self.send_json({"type": "end", "reason": reason, "winner": self.username})
                player_count = len(game.players)
                if player_count == 1:
                    winner_player = game.players[0]
                    winner_name = winner_player.username if hasattr(winner_player, "username") else str(winner_player)
                    print(f"🏆 Auto-win: Only player {winner_name} remains", flush=True)

                    reason = _("Game Over: %(winner)s wins") % {'winner': winner_name}
                    await self.send_json({"type": "end", "reason": reason, "winner": winner_name})
                    # optionally register winner to the tournament
                    if hasattr(self, "tournament_consumer"):
                        await self.tournament_consumer.register_match_result(game_id, winner_name)

                    # Clean up
                    # del games[game_id]
                elif player_count == 0:
                    print("🛑 Both players disconnected. No winner.", flush=True)
                    await self.send_json({
                        "type": "end",
                        "reason": _("Game Over: No players present"),
                        "winner": None
                    })
                    # del games[game_id]

                else:
                    print("⚠️ Unexpected state: Game auto-started with 2 players but none ready?", flush=True)

    async def game_created(self, event):
        game_id = event["game_id"]
        player1 = event["player1"]
        player2 = event["player2"]
        # self.tournament.matches.append((player1, player2, game_id))
        # print(f" {self.tournament.matches}", flush=True) 
        if not any(game_id == match[0] for match in self.tournament.matches):
            self.tournament.matches.append((game_id, player1, player2))

        print(f"Tournament match {game_id} added: {player1} vs {player2}.", flush=True)
        print(f"Current matches: {self.tournament.matches}", flush=True)
        if self.username in [player1, player2]: 
            await self.send_json({
                "type": "match_start",
                # "data": game.get_state()
            })
        await self.broadcast_tournament_state()

    async def game_result(self, event):
        game_id = event["game_id"]
        winner = event["winner"]
        winner_username = winner

        try:
            match = await sync_to_async(
                lambda: Match.objects.select_related("player_1", "player_2").get(id=game_id)
            )()
            logger.info(f"Match id: {match.id}, players: {match.player_1.username} vs {match.player_2.username}")
            if match.player_1.username == winner_username:
                match.winner = match.player_1
                match.player_1_points = 3
                match.player_2_points = 0
            elif match.player_2.username == winner_username:
                match.winner = match.player_2
                match.player_2_points = 3
                match.player_1_points = 0
            else:
                raise ValueError(f"Winner username {winner_username} not found in match")
            await sync_to_async(match.save)()
            logger.info("Match saved successfully")
        except Exception as e:
            logger.error(f"Error processing game result: {e}")

        # updates the tournament bracket
        await self.tournament.register_match_result(game_id, winner_username)
        
        # If tournament is finished, update the database record with the results
        if self.tournament.final_winner and hasattr(self, 'tournament_db_id'):
            tournament_db = await sync_to_async(Tournament.objects.get)(id=self.tournament_db_id)
            print("tournament_db object is fetched")

            if self.tournament.final_winner:
                winner_user = await sync_to_async(
                    lambda: CustomUser.objects.filter(username=self.tournament.final_winner["username"]).first()
                )()
                tournament_db.first_place = winner_user
                print(f"TOURNAMENTWINNERMII = {self.tournament.final_winner}")
                print(f"TOURNAMENTWINNER = {winner_user}")
                # winner_user = await sync_to_async(CustomUser.objects.get)(username=self.tournament.final_winner)

            tournament_db.end_date = timezone.now()
            print(f"TOURNAMENTENDDD = {tournament_db.end_date}")
            await sync_to_async(tournament_db.save)()

        await self.broadcast_tournament_state()
    
    async def game_end(self, event):
        if self.game_id in games:
            game = games[self.game_id]
            if game:
                game.clear_game()
        else:
            print(f"Game already cleared: {self.game_id}", flush=True)

        await self.send_json({"type": "end", "reason": event.get("reason")}) # needed?? might be double when called
        await self.broadcast_tournament_state()

    async def tournament_update(self, event):
        """Receives the tournament state update and sends it to the frontend"""
        await self.send_json(event["data"])

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

        if hasattr(self, 'tournament_db_id'):
            tournament_db = await sync_to_async(Tournament.objects.get)(id=self.tournament_db_id)
        else:
            print("No tournament_db_id found", flush=True)
            return  # or handle this error more explicitly -- IS THIS CORRECT?
        user1 = await get_user_by_id(player1_id)
        user2 = await get_user_by_id(player2_id)

        if self.player_id == player1_id:
            match = await sync_to_async(lambda: Match.objects.filter(
                Q(player_1=user1, player_2=user2, tournament=tournament_db) |
                Q(player_1=user2, player_2=user1, tournament=tournament_db)
            ).first())()

            if match is None:
                print(f"NEW MATCH GETTING CREATED", flush=True)
                match = await sync_to_async(Match.objects.create)(
                    player_1=user1,
                    player_2=user2,
                    tournament=tournament_db,
                    # match_start=datetime.now().replace(hour=14, minute=0, second=0, microsecond=0), # fix this timing??
                    match_start=datetime.now(),
                    match_time=timedelta(minutes=2),
                )
            else:
                print(f"MATCH WAS ALREADY EXISITING FOR SOME REASON", flush=True)

            # need to: int(self.match_name[6:]) ??? like in connect in consumer.py??
            self.game_id = match.id
            self.match_name = str(f"match_{match.id}")

            await self.channel_layer.group_add(self.match_name, self.channel_name)

            game = Game("Two Players (remote)")
            game.reset_game("Two Players (remote)")

            db_player1 = await sync_to_async(lambda: match.player_1)()
            db_player2 = await sync_to_async(lambda: match.player_2)()
            if db_player1.id < db_player2.id:
                left_player, right_player = db_player1, db_player2
            else:
                left_player, right_player = db_player2, db_player1

            game.add_player_tournament(left_player.id, left_player.username, as_player1=True)
            game.add_player_tournament(right_player.id, right_player.username, as_player1=False)
            game.status = "started"
            game.is_partOfTournament()
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
            print(f"Game {self.game_id} created for {db_player1.username} vs {db_player2.username}.", flush=True)

            await self.send_game_state(game)
            asyncio.create_task(self.broadcast_game_state(self.game_id))

            # start 1min timer for them to start the match else we trigger automatically
            asyncio.create_task(self.tournament1v1game_start_game_task(self.game_id))
        
        elif self.player_id == player2_id:
            retries = 5
            delay = 5  # 5sec
            for attempt in range(retries):
                await asyncio.sleep(1)
                try:
                    match = await sync_to_async(
                        lambda: Match.objects.filter(player_1=user1, player_2=user2, tournament=tournament_db).latest('match_time')
                    )()
                    # match = await sync_to_async(Match.objects.get)(player_1_id=player1_id, player_2_id=player2_id)
                    self.game_id = match.id
                    self.match_name = str(f"match_{match.id}")
                    await self.channel_layer.group_add(self.match_name, self.channel_name)

                    game = games.get(match.id)
                    if game:
                        game.status = "started"
                        await self.send_game_state(game)
                        asyncio.create_task(self.broadcast_game_state(self.game_id))
                        # start 1min timer for them to start the match else we trigger automatically
                        asyncio.create_task(self.tournament1v1game_start_game_task(self.game_id))
                    else:
                        print(f"Game for match {match.id} not found.", flush=True)
                    break
                except Match.DoesNotExist:
                    print(f"Match not found for player 2 with IDs: {player1_id}, {player2_id}. Retrying {retries - attempt - 1} more times...", flush=True)
                    await asyncio.sleep(delay)
            else:
                print("Failed to retrieve match after several attempts.", flush=True)

        else:
            print(f"Player {self.player_id} is part of this match but will not create the game.", flush=True)
        
        await self.broadcast_tournament_state()

    async def tournament_winners(self, event):
        await self.send_json({
            "type": "add_winners",
            "winners": [w['username'] for w in event['winners']],
            "round": event["round"]
        })

        print(f"[TOURNAMENT UPDATE] Sent winners to frontend: {[w['username'] for w in event['winners']]} (Round {event['round']})", flush=True)

    async def force_cache_update(self, event):
        print(f"PLAYER {self.player_id} MADE IT INTO FORCE_CACHE_UPDATE", flush=True)
        state = event["state"]

        self.tournament.set_tournament_state(msgspec.json.decode(state))

        print(f"(BACKEND FORCE_CACHE_UPDATE) of {self.player_id}: {state}", flush=True)

        cache.delete("tournament_state")
        cache.set("tournament_state", state)
        await self.channel_layer.group_send(
            "tournament_lobby",
            {
                "type": "tournament_update",
                "data": state,
            }
        )

    async def broadcast_tournament_state(self):
        if not self.tournament:
            return

        state = self.tournament.get_tournament_state()
        if hasattr(self, 'tournament_db_id'):
            state['tournament_db_id'] = self.tournament_db_id

        print(f"(BACKEND) Sending update: {state}", flush=True)

        serialized = msgspec.json.encode(state).decode("utf-8")
        cache.delete("tournament_state")
        cache.set("tournament_state", serialized)
        await self.channel_layer.group_send(
            "tournament_lobby",
            {
                "type": "tournament_update",
                "data": serialized,
            }
        )
        logger.info("Broadcasted tournament state.")

    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]

            while game.running:
                game.update_state()

                await self.send_game_state(game)
                await self.send_json({
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

                        await self.send_json({"type": "end", "reason": f"Game Over: {winner} wins", "winner": winner})
                        reason = _("Game Over: %(winner)s wins") % {'winner': winner}
                        await self.channel_layer.group_send(
                            self.match_name,
                            {
                                "type": "game.end",
                                "reason": reason
                            }
                        )
                        await self.channel_layer.group_send(
                            "tournament_lobby",
                            {
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

default_tournament_state = {
    "tournament_active": False,
    "players_in": 0,
    "remaining_spots": 4,
    "players": [],
    "bracket": {},
    "current_round": 1,
    "running": False,
    "final_winner": None,
    "matches": [],
    "winners": []
}  # Default state
