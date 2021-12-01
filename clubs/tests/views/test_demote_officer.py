"""Tests of the demote_officer view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class DemoteOfficerViewTestCase(TestCase,LogInTester):
    """Tests of the demote_officer view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.officer = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OWN'})
        self.club.club_members.add(self.officer,through_defaults={'club_role':'OFF'})
        self.url = reverse('demote_officer',kwargs={'club_name': self.club.club_name,'user_id':self.officer.id})

    def test_transfer_ownwership_url(self):
        self.assertEqual(self.url,f'/officers/{self.club.club_name}/demote_officer/{self.officer.id}/')

    def test_demote_officer_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_officers = Role.objects.all().filter(club=self.club,club_role='OFF').count()
        before_members = Role.objects.all().filter(club=self.club,club_role='MEM').count()
        before_demote_role = self.officer.role_set.get(club=self.club)
        self.assertEqual('OFF',before_demote_role.club_role)
        response = self.client.get(self.url)
        after_officers =  Role.objects.all().filter(club=self.club,club_role='OFF').count()
        after_members =  Role.objects.all().filter(club=self.club,club_role='MEM').count()
        self.assertEqual(before_officers,after_officers+1)
        self.assertEqual(before_members+1,after_members)
        after_demote_role = self.officer.role_set.get(club=self.club)
        self.assertEqual('MEM',after_demote_role.club_role)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'officer_list.html')
        self.assertNotContains(response, "Jane Doe")
        self.assertNotContains(response, "janedoe@example.org")

    def test_demote_officer_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_members = Role.objects.all().filter(club=self.club,club_role='MEM').count()
        url = reverse('demote_officer', kwargs={'club_name':self.club.club_name,'user_id': self.officer.id+9999})
        after_members = Role.objects.all().filter(club=self.club,club_role='MEM').count()
        self.assertEqual(before_members,after_members)
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')


    def test_demote_officer_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('demote_officer', kwargs={'club_name':'WRONG CLUB','user_id': self.officer.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_demote_officer_user_does_not_have_permission_is_officer(self):
        officer = User.objects.get(username='robertdoe@example.org')
        self.client.login(username=officer.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_demote_officer_user_does_not_have_permission_is_member(self):
        member = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(member,through_defaults={'club_role':'MEM'})
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_demote_officer_user_does_not_have_permission_is_applicant(self):
        applicant = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(applicant,through_defaults={'club_role':'APP'})
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')

    def test_demote_officer_user_does_not_have_permission_is_visitor(self):
        visitor_user = User.objects.get(username='robertdoe@example.org')
        self.client.login(username=visitor_user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response,response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response,'feed.html')



    def test_demote_officer_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
