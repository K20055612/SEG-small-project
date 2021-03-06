"""Tests of the unban_member view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class UnbanMemberViewTestCase(TestCase,LogInTester):
    """Tests of the unban_member view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.banned = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.banned,through_defaults={'club_role':'BAN'})
        self.url = reverse('unban_member',kwargs={'club_name': self.club.club_name,'user_id':self.banned.id})

    def test_unban_member_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/member_management/unban/{self.banned.id}/')

    def test_unban_member_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_banned = Role.objects.all().filter(club=self.club,club_role='BAN').count()
        response = self.client.get(self.url)
        after_banned =  Role.objects.all().filter(club=self.club,club_role='BAN').count()
        self.assertEqual(before_banned,after_banned+1)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.club.club_members.all().filter(id=self.banned.id,
            club__club_name = self.club.club_name).exists())

    def test_unban_member_as_owner(self):
        owner = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(owner,through_defaults={'club_role':'OWN'})
        self.client.login(username=owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_banned = Role.objects.all().filter(club=self.club,club_role='BAN').count()
        response = self.client.get(self.url)
        after_banned =  Role.objects.all().filter(club=self.club,club_role='BAN').count()
        self.assertEqual(before_banned,after_banned+1)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.club.club_members.all().filter(id=self.banned.id,
            club__club_name = self.club.club_name).exists())

    def test_unban_member_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before = Role.objects.all().filter(club=self.club,club_role='BAN').count()
        url = reverse('unban_member', kwargs={'club_name':self.club.club_name,'user_id': self.banned.id+9999})
        after = Role.objects.all().filter(club=self.club,club_role='BAN').count()
        self.assertEqual(before,after)
        role = self.banned.role_set.get(club=self.club)
        self.assertEqual('BAN',role.club_role)
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertTrue(self.club.club_members.all().filter(id=self.banned.id,
            club__club_name = self.club.club_name).exists())

    def test_unban_member_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('unban_member', kwargs={'club_name':'WRONG CLUB','user_id': self.banned.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_unban_member_user_does_not_have_permission_is_member(self):
        member = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'MEM'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_unban_member_user_does_not_have_permission_is_applicant(self):
        applicant = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(applicant,through_defaults={'club_role':'APP'})
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_unban_member_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='robertdoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_unban_member_user_does_not_have_permission_is_banned(self):
        banned_user = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(banned_user,through_defaults={'club_role':'BAN'})
        self.client.login(username=banned_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_unban_member_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
