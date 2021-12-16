"""Tests of the withdraw application view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class WithdrawApplicationViewTestCase(TestCase,LogInTester):
    """Tests of the withdraw application view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.applicant = User.objects.get(username='bobdoe@example.org')
        self.member = User.objects.get(username='janedoe@example.org')
        self.officer = User.objects.get(username='robertdoe@example.org')
        self.owner = User.objects.get(username='patrickdoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.applicant,through_defaults={'club_role':'APP'})
        self.club.club_members.add(self.officer,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.member,through_defaults={'club_role':'MEM'})
        self.club.club_members.add(self.owner,through_defaults={'club_role':'OWN'})
        self.url = reverse('withdraw_application',kwargs={'club_name': self.club.club_name, 'user_id': self.applicant.id})

    def test_withdraw_application_url(self):
        self.assertEqual(self.url,f'/withdraw_application/{self.club.club_name}/{self.applicant.id}/')

    def test_withdraw_from_valid_club(self):
        self.client.login(username=self.applicant.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before_applicants,after_applicants+1)
        self.assertEqual(response.status_code, 302)

    def test_withdraw_from_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        url = reverse('withdraw_application', kwargs={'club_name':'WRONG CLUB', 'user_id': self.user.id})
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before_applicants,after_applicants)
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdrawn_user_can_only_withdraw_once_per_club(self):
         self.client.login(username=self.user.username, password='Password123')
         self.assertTrue(self._is_logged_in())
         before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
         url = reverse('withdraw_application', kwargs={'club_name':'WRONG CLUB','user_id': self.user.id})
         response = self.client.get(url,follow=True)
         after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
         self.assertEqual(before_applicants,after_applicants)
         response = self.client.get(self.url, follow=True)
         response_url = reverse('feed')
         self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdraw_members_cannot_withdraw_from_same_club(self):
        self.client.login(username=self.member.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_members = Role.objects.all().filter(club=self.club,club_role='MEM').count()
        url = reverse('withdraw_application', kwargs={'club_name':'WRONG CLUB','user_id': self.member.id})
        response = self.client.get(url,follow=True)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_members = Role.objects.all().filter(club=self.club,club_role='MEM').count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_members,after_members)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdraw_officers_cannot_withdraw_from_same_club(self):
        self.client.login(username=self.officer.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_officers = Role.objects.all().filter(club=self.club,club_role='OFF').count()
        url = reverse('withdraw_application', kwargs={'club_name':'WRONG CLUB','user_id': self.officer.id})
        response = self.client.get(url,follow=True)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_officers = Role.objects.all().filter(club=self.club,club_role='OFF').count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_officers,after_officers)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdraw_owners_cannot_withdraw_from_same_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_owner = Role.objects.all().filter(club=self.club,club_role='OWN').count()
        url = reverse('withdraw_application', kwargs={'club_name':'WRONG CLUB','user_id': self.owner.id})
        response = self.client.get(url,follow=True)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_owner = Role.objects.all().filter(club=self.club,club_role='OWN').count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_owner,after_owner)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdraw_application_applicant_does_not_exist(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('withdraw_application', kwargs={'club_name': self.club.club_name,'user_id': 99999})
        response = self.client.get(url,follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_withdraw_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
