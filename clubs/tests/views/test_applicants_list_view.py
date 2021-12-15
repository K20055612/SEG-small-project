
"""Unit tests for the applicant list view"""

from django.test import TestCase
from clubs.models import User,Club,Role
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next


class ApplicantListViewTestCase(TestCase,LogInTester):
    """Unit tests for the applicant list."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_users.json',
    'clubs/tests/fixtures/other_clubs.json']


    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.url = reverse('applicants_list',kwargs={'club_name': self.club.club_name})

    def test_applicant_list_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/applicants/')

    def test_get_applicant_list_with_applicants(self):
        self.client.login(username=self.user.username, password='Password123')
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

    def test_get_applicant_list_with_no_applicants(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 0)
        for user_id in range(15-1):
            self.assertNotContains(response, f'user{user_id}')
            self.assertNotContains(response, f'First{user_id}')
            self.assertNotContains(response, f'Last{user_id}')

    def test_get_applicant_list_as_owner(self):
        owner = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(owner,through_defaults={'club_role':'OWN'})
        self.client.login(username=owner.username, password='Password123')
        self._create_test_applicants(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 14)
        for user_id in range(15-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')

    def test_applicant_list_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('applicants_list', kwargs={'club_name':'Wrong Club'})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_applicant_list_user_does_not_have_permission_is_member(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'MEM'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_applicant_list_user_does_not_have_permission_is_banned(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'BAN'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_applicant_list_user_does_not_have_permission_is_applicant(self):
        applicant = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(applicant,through_defaults={'club_role':'APP'})
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_applicant_list_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='janedoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_applicant_list_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in',self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_applicants(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                username=f'user{user_id}@test.org',
                password='Password123',
                bio=f'Bio {user_id}',
                chess_experience_level = 1,
            )
            self.club.club_members.add(user,through_defaults={'club_role':'APP'})
