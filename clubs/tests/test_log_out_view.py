"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from .helpers import LogInTester
from clubs.forms import LogInForm

class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view."""

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user('@alicedoe',
            first_name='Alice',
            last_name='Doe',
            email='alicedoe@example.org',
            bio='Hello, I am Alice Doe.',
            chess_experience_level=1,
            is_member=False,
            is_officer=False,
            is_owner=False,
            password='Password123',
            is_active=True,
        )

    def test_log_out_url(self):
        self.assertEqual(self.url,'/log_out/')

    def test_get_log_out(self):
        self.client.login(username='alicedoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())