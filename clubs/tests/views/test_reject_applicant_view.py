"""Tests of the reject_applicant view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class RejectApplicantViewTestCase(TestCase,LogInTester):
    """Tests of the reject_applicant view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.applicant = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.applicant,through_defaults={'club_role':'APP'})
        self.url = reverse('reject_applicant',kwargs={'club_name': self.club.club_name,'user_id':self.applicant.id})


    def test_reject_applicant_url(self):
        self.assertEqual(self.url,f'/applicants/{self.club.club_name}/reject/{self.applicant.id}/')

    def test_reject_applicant_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before = Role.objects.all().filter(club=self.club,club_role='APP').count()
        response = self.client.get(self.url)
        after =  Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before,after+1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe")

    def test_reject_applicant_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before = Role.objects.all().filter(club=self.club,club_role='APP').count()
        url = reverse('reject_applicant', kwargs={'club_name':self.club.club_name,'user_id': self.applicant.id+9999})
        after = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before,after)
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_reject_applicant_user_does_not_have_permission_is_member(self):
        invalid_permission_user = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(invalid_permission_user,through_defaults={'club_role':'MEM'})
        self.client.login(username=invalid_permission_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')


    def test_reject_applicant_user_does_not_have_permission_is_applicant(self):
        invalid_permission_user = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(invalid_permission_user,through_defaults={'club_role':'APP'})
        self.client.login(username=invalid_permission_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_reject_applicant_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='janedoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_reject_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
