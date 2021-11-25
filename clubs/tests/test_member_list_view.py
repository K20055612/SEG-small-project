"""Unit tests for the member list view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from .helpers import reverse_with_next

class MemberListTestCase(TestCase):
    """Unit tests for the member list."""

    fixtures = [
        'clubs/tests/fixtures/member_user.json',
    ]

    def setUp(self):
        self.url = reverse('member_list')
        self.user = User.objects.get(username='bobdoe')

    def test_member_list_url(self):
        self.assertEqual(self.url,'/members/')

    def test_get_member_list(self):
        self.client.login(username=self.user.email, password='Password123')
        self._create_test_members(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['members']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')

    def test_get_member_list_view_redirects_when_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_members(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                email=f'user{user_id}@test.org',
                username = f'user{user_id}',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
                is_applicant = True,
                is_member = True,
                is_officer = False,
                is_owner = False,
            )
