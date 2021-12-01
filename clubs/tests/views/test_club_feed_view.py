"""Unit tests for the club feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import reverse_with_next,LogInTester

class ClubFeedTestCase(TestCase,LogInTester):
    """Unit tests for the club feed view."""

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
            self.url = reverse('club_feed',kwargs={'club_name': self.club.club_name})

    def test_club_feed_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/feed')

    def test_get_club_feed_as_member(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_officer'])
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(len(response.context['members']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')

    def test_get_club_feed_as_officer(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        role = Role.objects.get(user=self.user,club=self.club,club_role='MEM')
        role.toggle_officer()
        self._create_test_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_officer'])
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(len(response.context['members']), 14)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')

    def test_get_member_club_feed_redirects_when_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_members(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                username=f'user{user_id}@test.org',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,

            )
            self.club.club_members.add(user,through_defaults={'club_role':'MEM'})
