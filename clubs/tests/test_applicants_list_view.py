
"""Unit tests for the applicant list view"""

from django.test import TestCase
from clubs.models import User,Club,Role
from django.urls import reverse
from .helpers import LogInTester,reverse_with_next


class ApplicantListViewTestCase(TestCase,LogInTester):
    """Unit tests for the applicant list."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(club_name='Beatles')
        self.url = reverse('applicants_list',kwargs={'club_name': self.club.club_name})

    def test_applicant_list_url(self):
        self.assertEqual(self.url,f'/applicants/{self.club.club_name}/')

    def test_get_applicant_list(self):
        self.client.login(username=self.user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_applicants(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 14)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')


    def _create_test_applicants(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                email=f'user{user_id}@test.org',
                username = f'user{user_id}',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
            )
            self.club.club_members.add(user,through_defaults={'club_role':'APP'})
