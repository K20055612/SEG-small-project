"""Tests of the delete_club view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next

class DeleteClubViewTestCase(TestCase,LogInTester):
    """Tests of the delete_club view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OWN'})
        self.url = reverse('delete_club',kwargs={'club_name': self.club.club_name})

    def test_delete_club_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/delete')

    def test_delete_valid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = Club.objects.count()
        response = self.client.get(self.url)
        after_count = Club.objects.count()
        self.assertEqual(before_count,after_count+1)
        response_url = reverse('feed')
        self.assertTemplateUsed(response, 'feed.html')
        for club_id in range(3-1):
            self.assertNotContains(response, self.club.club_name)


    def test_delete_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('delete_club', kwargs={'club_name':'Wrong Club'})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        for club_id in range(3-1):
            self.assertContains(response, self.club.club_name)

    def test_delete_club_user_does_not_have_permission_is_officer(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'OFF'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_delete_club_user_does_not_have_permission_is_member(self):
        member = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'MEM'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_delete_club_user_does_not_have_permission_is_applicant(self):
        applicant = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(applicant,through_defaults={'club_role':'APP'})
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_delete_club_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='janedoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_delete_club_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in',self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
