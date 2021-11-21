"""Unit tests for the main feed view"""
from django.test import TestCase
from clubs.models import User
from django.urls import reverse


class MainFeedTestCase(TestCase):
    """Unit tests for the main feed."""

    fixtures = [
        'clubs/tests/fixtures/member_user.json',
        'clubs/tests/fixtures/officer_user.json',
        'clubs/tests/fixtures/owner_user.json',
        'clubs/tests/fixtures/applicant_user.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='bobdoe')
        self.url = reverse('main_feed')

    def test_main_feed_url(self):
        self.assertEqual(self.url,'/feed/')

    def test_officer_get_feed(self):
        officer_user = User.objects.get(username='johndoe')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'officer_feed.html')

    # def test_get_main_feed_redirects_when_user_not_logged_in(self):
    #     redirect_url = reverse_with_next('log_in', self.url)
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
