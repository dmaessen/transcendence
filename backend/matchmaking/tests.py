from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from data.models import User, Match

class MatchViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        User.objects.create(name="player1")
        User.objects.create(name="player2")

    def test_join_queue(self):
        response = self.client.post(reverse('join_queue'), {
            'name': 'player3',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 3)

    def test_create_match(self):
        response = self.client.post(reverse('create_matches'), {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Match.objects.count(), 1)

        match = Match.objects.first()
        self.assertEqual(match.player_1.name, "player1")
        self.assertEqual(match.player_2.name, "player2")

    def test_create_match_fails(self):
        User.objects.all().delete()
        User.objects.create(name="player3")

        response = self.client.post(reverse("create_matches"), {}, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Match.objects.count(), 0)


    def test_list_players(self):
        response = self.client.get(reverse('list_players'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.filter(name="player1").exists(), True)
        self.assertEqual(User.objects.filter(name="player2").exists(), True)

        self.client.post(reverse('join_queue'), {
            'name': 'player4',
        }, format='json')

        self.assertEqual(User.objects.filter(name="player4").exists(), True)

    def test_list_matches(self):
        #add 2 more player to test db
        User.objects.create(name="player5")
        User.objects.create(name="player6")
        self.assertEqual(User.objects.count(), 4)
        
        self.client.post(reverse('create_matches'), {}, format='json')

        response = self.client.get(reverse('matches'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Match.objects.count(), 2)

