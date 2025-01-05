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
        response = self.client.post(reverse('create_matches'), {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Match.objects.count(), 1)

        match = Match.objects.first()
        self.assertEqual(match.player1, "player2")
        self.assertEqual(match.player2, "player1")

    def test_create_match_fails(self):
        PlayerQueue.objects.all().delete()
        PlayerQueue.objects.create(player_id="player3", total_wins=8)

        response = self.client.post(reverse("create_matches"), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Match.objects.count(), 0)


    def test_list_players(self):
        response = self.client.get(reverse('list_players'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PlayerQueue.objects.count(), 2)
        self.assertEqual(PlayerQueue.objects.filter(player_id="player1").exists(), True)
        self.assertEqual(PlayerQueue.objects.filter(player_id="player2").exists(), True)

        self.client.post(reverse('join_queue'), {
            'player_id': 'player4',
            'total_wins': 3
        }, format='json')

        self.assertEqual(PlayerQueue.objects.filter(player_id="player4").exists(), True)

    def test_list_matches(self):
        #add 2 more player to test db
        PlayerQueue.objects.create(player_id="player5", total_wins=4)
        PlayerQueue.objects.create(player_id="player6", total_wins=5)
        self.assertEqual(PlayerQueue.objects.count(), 4)
        
        self.client.post(reverse('create_matches'), {}, format='json')

        response = self.client.get(reverse('matches'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Match.objects.count(), 2)


