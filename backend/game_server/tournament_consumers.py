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

class TournamentConsumer(AsyncWebsocketConsumer):
    tournament = None  # keeps track of the tournament instance
    initiator = None

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
        elif action == "match_ready":
            await self.handle_match_ready(data)
        elif action == "report_match":
            await self.handle_report_match(data)
        elif action == "disconnect":
            await self.handle_disconnect(data)
        else:
            print(f"Unknown action: {action}")

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    async def handle_connect(self, data):
        mode = data.get("mode")  # 4 or 8 players
        print(f"Player {self.player_id} connected to {mode}-player tournament.")

    async def handle_start_tournament(self, data):
        """Start the tournament when enough players have joined."""
        mode = data.get("mode")
        self.initiator = self.player_id
        self.tournament = Tournament(mode=mode)
        print(f"Starting a {mode}-player tournament. Initiator: {self.initiator}")
        await self.broadcast_tournament_state()

    # async def handle_join_tournament(self, data):
    #     """Player wants to join the tournament."""
    #     if self.tournament:
    #         if len(self.tournament.players) < self.tournament.num_players:
    #             self.tournament.add_player(self.player_id)
    #             await self.broadcast_tournament_state()
    #             print(f"Player {self.player_id} joined the tournament.")
    #             if len(self.tournament.players) == self.tournament.num_players:
    #                 print(f"Tournament started in handle_join_tournament")
    #                 tournament.start_tournament() # follow from here where it gpes next and what to do
    #                 await self.broadcast_tournament_state()
    #         else:
    #             self.tournament_full()
    #             print(f"Tournament is full. Player {self.player_id} cannot join.")

    async def handle_join_tournament(self, data):
        tournament_state = cache.get('tournament_state')
        if tournament_state:
            tournament_state = json.loads(tournament_state)
            self.tournament = Tournament(mode=tournament_state['mode'])
            self.tournament.players = tournament_state['players']
        else:
            self.tournament = Tournament(mode=data.get("mode"))

        if len(self.tournament.players) < self.tournament.num_players:
            self.tournament.add_player(self.player_id)
            print(f"Player {self.player_id} joined the tournament.")
            await self.broadcast_tournament_state()
            if len(self.tournament.players) == self.tournament.num_players:
                print(f"Tournament starting from handle_join_tournament")
                self.tournament.start_tournament()
                await self.broadcast_tournament_state()
        else:
            await self.tournament_full()
            print(f"Tournament is full. Player {self.player_id} cannot join.")

    async def handle_leave_tournament(self, data):
        """Player leaves before the tournament starts."""
        if self.tournament and self.player_id in self.tournament.players:
            self.tournament.players.remove(self.player_id)
            await self.broadcast_tournament_state()
        print(f"Player {self.player_id} left the tournament.")

    async def handle_match_ready(self, data):
        """Acknowledge that the player is ready for their match."""
        print(f"Player {self.player_id} is ready for their match.")

    async def handle_report_match(self, data):
        """Report the match result."""
        game_id = data.get("game_id")
        winner = data.get("winner")
        print(f"Game {game_id} finished. Winner: {winner}")

    async def handle_disconnect(self, data):
        """Handle player disconnection."""
        print(f"Player {self.player_id} disconnected from tournament.")

    async def tournament_full(self):
        await self.send_json({
            "type": "tournament_full"
        })

    async def tournament_update(self, event):
        """Receives the tournament state update and sends it to the frontend"""
        await self.send(text_data=event["message"])

    async def broadcast_tournament_state(self):
        """Broadcasts the current tournament state to all connected clients"""
        if self.tournament:
            # state = {
            #     "action": "update_tournament",
                
            #     "players_in": len(self.tournament.players),
            #     "remaining_spots": self.tournament.num_players - len(self.tournament.players),
            # }
            state = self.tournament.get_tournament_state()
            state["action"] = "update_tournament"

            print(f"(BACKEND) Sending update: {state}", flush=True)
            # cache.set("tournament_state", state) # was working
            cache.set("tournament_state", json.dumps(state))

            await self.channel_layer.group_send(
                self.room_name, {
                    "type": "tournament_update",
                    "message": json.dumps(state)
                }
            )
