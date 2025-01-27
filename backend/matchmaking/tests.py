from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from . import game_state
from data.models import User, Match

class MatchViewTest(TestCase):
    def setUp(self):
        global player_queue  # Import the global queue to ensure it’s empty at the start
        player_queue = []

        self.client = APIClient()

        # create two test users
        self.user1 = User.objects.create_user(email="user1@example.com", password="password123", name="User1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password123", name="User2")

    def test_create_a_match(self):
        response = self.client.post(reverse('create_a_match'), {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Match.objects.count(), 1)

        match = Match.objects.first()
        self.assertEqual(match.player_1.email, "user1@example.com")
        self.assertEqual(match.player_2.email, "user2@example.com")

    def test_create_match_fails(self):
        User.objects.all().delete()
        User.objects.create_user(email="user3@example.com", password="password123", name="User3")

        response = self.client.post(reverse("create_matches"), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Match.objects.count(), 0)


    def test_list_players(self):
        response = self.client.get(reverse('list_players'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.filter(name="User1").exists(), True)
        self.assertEqual(User.objects.filter(name="User2").exists(), True)


    def test_list_matches(self):
        #add 2 more player to test db
        User.objects.create_user(email="user5@example.com", password="password123", name="User5")
        User.objects.create_user(email="user6@example.com", password="password123", name="User6")
        self.assertEqual(User.objects.count(), 4)
        
        self.client.post(reverse('create_matches'), {}, format='json')

        response = self.client.get(reverse('matches'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Match.objects.count(), 2)

