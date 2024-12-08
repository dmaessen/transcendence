from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import PlayerQueue, Match

class MatchViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        PlayerQueue.objects.create(player_id="player1", total_wins=10)
        PlayerQueue.objects.create(player_id="player2", total_wins=8)
    
    def test_join_queue(self):
        response = self.client.post(reverse('join_queue'), {
            'player_id': 'player3',
            'total_wins': 3
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(PlayerQueue.objects.count(), 3)

    def test_create_match(self):
        response = self.client.post(reverse('create_match'), {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Match.objects.count(), 1)

        match = Match.objects.first()
        self.assertEqual(match.player1, "player1")
        self.assertEqual(match.player2, "player2")