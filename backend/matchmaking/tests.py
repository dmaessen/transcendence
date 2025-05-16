from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import timedelta
from datetime import datetime

from .game_state import player_queue
from data.models import CustomUser, Match

class MatchViewTest(TestCase):
    def setUp(self):
        #global player_queue

        self.client = APIClient()

        # create two test users
        self.user1 = CustomUser.objects.create_user(email="user1@example.com", password="password123", name="User1")
        self.user2 = CustomUser.objects.create_user(email="user2@example.com", password="password123", name="User2")

    def test_create_a_match(self):
        self.client.force_authenticate(user=self.user1)
        self.client.force_authenticate(user=self.user2)

        response = self.client.post(reverse('create_a_match'), {}, format='json')
        
        # Only one player asked for a match, we have one player in queue
        self.assertEqual(Match.objects.count(), 0)
        self.assertEqual(response.status_code, 404)

        # Another player asked for a match, not match will be made
        response = self.client.post(reverse('create_a_match'), {}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(PlayerQueue.objects.count(), 3)

    def test_create_match(self):
        response = self.client.post(reverse('create_matches'), {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Match.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

        match = Match.objects.first()
        self.assertEqual(match.player_1.email, "user2@example.com")
        self.assertEqual(match.player_2.email, "user2@example.com")

    def test_create_match_fails(self):
        CustomUser.objects.all().delete()
        self.assertEqual(CustomUser.objects.count(), 0)

        user3 = CustomUser.objects.create_user(email="user3@example.com", password="password123", name="User3")
        self.client.force_authenticate(user=user3)

        self.assertEqual(CustomUser.objects.count(), 1)
        response = self.client.post(reverse("create_matches"), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Match.objects.count(), 0)


    def test_create_match_fails(self):
        PlayerQueue.objects.all().delete()
        PlayerQueue.objects.create(player_id="player3", total_wins=8)

        response = self.client.post(reverse("create_matches"), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Match.objects.count(), 0)


    def test_list_players(self):
        response = self.client.get(reverse('list_players'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(CustomUser.objects.filter(name="User1").exists(), True)
        self.assertEqual(CustomUser.objects.filter(name="User2").exists(), True)

        user3 = CustomUser.objects.create_user(email="user3@example.com", password="password123", name="User3")
        response = self.client.get(reverse('list_players'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 3)
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
