"""Unit tests for the officer list view"""

from django.test import TestCase
from clubs.models import User,Club,Role
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next


class OfficerListViewTestCase(TestCase,LogInTester):
    """Unit tests for the officer list."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OWN'})
        self.url = reverse('officer_list',kwargs={'club_name': self.club.club_name})

    def test_applicant_list_url(self):
        self.assertEqual(self.url,f'/officers/{self.club.club_name}/')

    def test_get_officer_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self._create_test_officers(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'officer_list.html')
        self.assertEqual(len(response.context['officers']), 14)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')

    def test_officer_list_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('officer_list', kwargs={'club_name':'Wrong Club'})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_officer_list_user_does_not_have_permission_is_member(self):
        invalid_permission_user = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(invalid_permission_user,through_defaults={'club_role':'MEM'})
        self.client.login(username=invalid_permission_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def _create_test_officers(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                username=f'user{user_id}@test.org',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
            )
            self.club.club_members.add(user,through_defaults={'club_role':'OFF'})
