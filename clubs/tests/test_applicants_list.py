"""Unit tests for the officer feed view"""
from django.test import TestCase
from clubs.models import User
from django.urls import reverse


class OfficerFeedTestCase(TestCase):
    """Unit tests for the officer feed."""

    fixtures = ['clubs/tests/fixtures/officer_user.json']

    def setUp(self):
        self.url = reverse('applicants_list')
        self.user = User.objects.get(username='johndoe')

    def test_main_officer_feed_url(self):
        self.assertEqual(self.url,'/applicants/')

    def test_officer_get_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')

    def test_get_applicant_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_applicants(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 14)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            #user = User.objects.get(username=f'@user{user_id}')

    def _create_test_applicants(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                email=f'user{user_id}@test.org',
                username = f'user{user_id}',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
                is_member = False,
                is_officer = False,
                is_owner = False,
            )

    # def test_get_members_list(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     self._create_test_members(14)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'officer_feed.html')
    #     self.assertEqual(len(response.context['members']), 14)
    #     for user_id in range(14):
    #         self.assertContains(response, f'user{user_id}')
    #         self.assertContains(response, f'First{user_id}')
    #         self.assertContains(response, f'Last{user_id}')
    #
    # def _create_test_members(self, user_count):
    #     for user_id in range(user_count):
    #         User.objects.create_user(
    #             first_name=f'First{user_id}',
    #             last_name=f'Last{user_id}',
    #             email=f'user{user_id}@test.org',
    #             username = f'user{user_id}',
    #             password='Password123',
    #             bio=f'Bio {user_id}',
    #             chess_experience_level = 2,
    #             is_member = True,
    #             is_officer = False,
    #             is_owner = False,
    #         )

    # def test_get_main_feed_redirects_when_user_not_logged_in(self):
    #     redirect_url = reverse_with_next('log_in', self.url)
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
