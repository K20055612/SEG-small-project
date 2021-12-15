"""Tests of the search_member view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next
from django.test.client import Client

class SearchMemberTestCase(TestCase,LogInTester):
    """Tests of the search_member view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.member = User.objects.get(username = 'bobdoe@example.org')
        self.visitor = User.objects.get(username = 'janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.member,through_defaults={'club_role':'MEM'})
        self.url = reverse('search_member',kwargs={'club_name': self.club.club_name})
        self.form_input = {
            'member_name':'Bob'
        }


    def test_search_member_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/search_member/')

    def test_search_for_valid_member(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_member.html')
        self.assertEqual(len(response.context['members']), 1)
        self.assertContains(response, 'Bob Doe')
        self.assertTemplateUsed(response, 'search_member.html')

    def test_search_for_invalid_member(self):
        self.form_input['member_name'] = 'Jane'
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_member.html')
        self.assertEqual(len(response.context['members']), 0)
        self.assertNotContains(response, 'Jane Doe')
        self.assertTemplateUsed(response, 'search_member.html')

    def test_search_member_user_not_in_club(self):
        self.client.login(username=self.visitor.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,self.form_input,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_search_member_input_is_empty(self):
        self.form_input['member_name'] = ''
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,self.form_input,follow=True)
        response_url = reverse('club_feed',kwargs={'club_name':self.club.club_name})
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'club_feed.html')

    def test_delete_club_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in',self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
