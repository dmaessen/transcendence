import os
import csv
from django.conf import settings
from django.test import TestCase
from .models import User

class UserModelFromFileTest(TestCase):
    def setUp(self):
        # Path to your test file
        self.file_path = '/app/data/test_data/users.csv'
        # Read the file and create users in the test database
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.create(
                    name=row['name'],
                    location=row['location'],
                    score=int(row['score']),
                    victories=int(row['victories'])
                )
    
    def test_users_created(self):
        # Check the number of users created
        self.assertEqual(User.objects.count(), 7)
        
        # Validate a specific user's data
        user = User.objects.get(name="Alice")
        self.assertEqual(user.location, "New York")
        self.assertEqual(user.score, 150)
        self.assertEqual(user.victories, 10)
