"""Unit tests for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import reverse_with_next,LogInTester

class FeedTestCase(TestCase,LogInTester):
    """Unit tests for the feed view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
            self.user = User.objects.get(username='johndoe@example.org')
            self.club = Club.objects.get(club_name='Beatles')
            self.applied_to_club = Club.objects.get(club_name='EliteChess')
            self.club.club_members.add(self.user,through_defaults={'club_role':'MEM'})
            self.applied_to_club.club_members.add(self.user,through_defaults={'club_role':'APP'})
            self.url = reverse('feed')

    def test_feed_url(self):
        self.assertEqual(self.url,'/feed/')

    def test_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertEqual(len(response.context['clubs']), 3)
        self.assertEqual(len(response.context['user_clubs']), 1)
        self.assertEqual(len(response.context['user_applicant_clubs']), 1)
