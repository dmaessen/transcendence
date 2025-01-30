import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.tournament_logic import Tournament

tournaments = {}  # active tournaments

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.channel_name
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_tournament":
            mode = int(data.get("mode"))
            tournament = tournaments.get(mode, Tournament(mode))
            tournaments[mode] = tournament
            await tournament.add_player(self.player_id, self)

    async def disconnect(self, close_code):
        for tournament in tournaments.values():
            tournament.remove_player(self.player_id)
