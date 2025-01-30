class Tournament:
    def __init__(self, size): # something else we need here no?? 
        self.size = size
        self.players = []
        self.matches = {}

    async def add_player(self, player_id, consumer):
        self.players.append((player_id, consumer))

        if len(self.players) == self.size:
            await self.create_bracket()

    async def create_bracket(self): # but this is on Gul right???
        """Pairs players into matches"""
        for i in range(0, len(self.players), 2):
            game_id = f"tournament_match_{i//2}"
            player1, player2 = self.players[i], self.players[i + 1]

            self.matches[game_id] = (player1, player2)
            await player1[1].send_json({"action": "match_found", "game_id": game_id})
            await player2[1].send_json({"action": "match_found", "game_id": game_id})

    def remove_player(self, player_id):
        self.players = [p for p in self.players if p[0] != player_id]
