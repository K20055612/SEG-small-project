"""Unit tests for the club welcome view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import reverse_with_next,LogInTester

class ClubFeedTestCase(TestCase,LogInTester):
    """Unit tests for the club welcome view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
            self.user = User.objects.get(username='johndoe@example.org')
            self.club = Club.objects.get(club_name='Beatles')
            self.url = reverse('club_welcome',kwargs={'club_name': self.club.club_name})

    def test_club_feed_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/')

    def test_get_club_welcome_as_new_user(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_applicant'])
        self.assertTemplateUsed(response, 'club_welcome.html')

    def test_get_club_welcome_as_applicant(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.club.club_members.add(self.user,through_defaults={'club_role':'APP'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_applicant'])
        self.assertTemplateUsed(response, 'club_welcome.html')

    def test_get_member_club_feed_redirects_when_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
