"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import UserForm
from clubs.models import User

class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/applicant_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='josedoe')
        self.url = reverse('profile')
        self.form_input = {
            'first_name': 'Jose2',
            'last_name': 'Doe2',
            'username': 'josedoe2',
            'email': 'josedoe2@example.org',
            'bio': 'New bio',
            'chess_experience_level': 3,
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.user)

#    def test_get_profile_redirects_when_not_logged_in(self):
#        redirect_url = reverse_with_next('log_in', self.url)
#        response = self.client.get(self.url)
#        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(username=self.user.email, password='Password123')
        self.form_input['username'] = 'BA'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'josedoe')
        self.assertEqual(self.user.first_name, 'Jose')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'josedoe@example.org')
        self.assertEqual(self.user.bio, "Hello, I am Jose Doe.")
        self.assertEqual(self.user.chess_experience_level, 1)

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.email, password='Password123')
        self.form_input['username'] = 'alicedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'josedoe')
        self.assertEqual(self.user.first_name, 'Jose')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'josedoe@example.org')
        self.assertEqual(self.user.bio, "Hello, I am Jose Doe.")
        self.assertEqual(self.user.chess_experience_level, 1)

    def test_succesful_profile_update(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'josedoe2')
        self.assertEqual(self.user.first_name, 'Jose2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'josedoe2@example.org')
        self.assertEqual(self.user.bio, 'New bio')
        self.assertEqual(self.user.chess_experience_level, 3)

#    def test_post_profile_redirects_when_not_logged_in(self):
#        redirect_url = reverse_with_next('log_in', self.url)
#        response = self.client.post(self.url, self.form_input)
#        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
