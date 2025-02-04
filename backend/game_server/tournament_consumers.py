import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game
from game_server.tournament_logic import Tournament

class TournamentConsumer(AsyncWebsocketConsumer):
    tournament = None  # keeps track of the tournament instance
    initiator = None

    async def connect(self):
        # self.player_id = self.scope["user"].id  # to ensure this is an integer, I use this in view as int
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

    async def handle_connect(self, data):
        """Handle player connection to the tournament."""
        player_id = data.get("player_id")
        mode = data.get("mode")  # 4 or 8 players
        print(f"Player {player_id} connected to {mode}-player tournament.")

    async def handle_start_tournament(self, data):
        """Start the tournament when enough players have joined."""
        mode = data.get("mode")
        self.initiator = data.get("player_id")
        self.tournament = Tournament(mode=mode)
        print(f"Starting a {mode}-player tournament. Initiator: {self.initiator}")
        await self.broadcast_tournament_state()

    async def handle_join_tournament(self, data):
        """Player wants to join the tournament."""
        player_id = data.get("player_id")
        if self.tournament:
            if len(self.tournament.players) < self.tournament.num_players:
                self.tournament.add_player(player_id)
                await self.broadcast_tournament_state()
                print(f"Player {player_id} joined the tournament.")
            else:
                print(f"Tournament is full. Player {player_id} cannot join.")

    async def handle_leave_tournament(self, data):
        """Player leaves before the tournament starts."""
        player_id = data.get("player_id")
        if self.tournament and player_id in self.tournament.players:
            self.tournament.players.remove(player_id)
            await self.broadcast_tournament_state()
        print(f"Player {player_id} left the tournament.")

    async def handle_match_ready(self, data):
        """Acknowledge that the player is ready for their match."""
        player_id = data.get("player_id")
        print(f"Player {player_id} is ready for their match.")

    async def handle_report_match(self, data):
        """Report the match result."""
        game_id = data.get("game_id")
        winner = data.get("winner")
        print(f"Game {game_id} finished. Winner: {winner}")

    async def handle_disconnect(self, data):
        """Handle player disconnection."""
        player_id = data.get("player_id")
        print(f"Player {player_id} disconnected from tournament.")

    async def tournament_update(self, event):
        """Receives the tournament state update and sends it to the frontend"""
        await self.send(text_data=event["message"])

    async def broadcast_tournament_state(self):
        """Broadcasts the current tournament state to all connected clients"""
        if self.tournament:
            state = {
                "action": "update_tournament",
                "players_in": len(self.tournament.players),
                "remaining_spots": self.tournament.num_players - len(self.tournament.players),
            }
            await self.channel_layer.group_send(
                self.room_name, {"type": "tournament_update", "message": json.dumps(state)}
            )
