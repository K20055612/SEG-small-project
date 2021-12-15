"""Tests of the apply_to_club view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class ApplyViewTestCase(TestCase,LogInTester):
    """Tests of the apply_to_club view."""

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
        self.url = reverse('apply_to_club',kwargs={'club_name': self.club.club_name})

    def test_apply_to_club_url(self):
        self.assertEqual(self.url,f'/apply/{self.club.club_name}/')

    def test_apply_to_valid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before_applicants+1,after_applicants)
        role = self.club.get_club_role(self.user)
        self.assertEqual(role,'APP')
        self.assertEqual(response.status_code, 302)

    def test_apply_to_invalid_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        url = reverse('apply_to_club', kwargs={'club_name':'WRONG CLUB'})
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        self.assertEqual(before_applicants,after_applicants)
        response = self.client.get(url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_user_can_only_apply_once_per_club(self):
         self.client.login(username=self.applicant.username, password='Password123')
         self.assertTrue(self._is_logged_in())
         before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
         response = self.client.get(self.url)
         after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
         self.assertEqual(before_applicants,after_applicants)
         response = self.client.get(self.url, follow=True)
         response_url = reverse('feed')
         self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
         self.assertTemplateUsed(response, 'feed.html')

    def test_apply_members_cannot_apply_to_same_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_all_members = Role.objects.all().filter(club=self.club).count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_all_members = Role.objects.all().filter(club=self.club).count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_all_members,after_all_members)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_officers_cannot_apply_to_same_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_all_members = Role.objects.all().filter(club=self.club).count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_all_members = Role.objects.all().filter(club=self.club).count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_all_members,after_all_members)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_owners_cannot_apply_to_same_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_all_members = Role.objects.all().filter(club=self.club).count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_all_members = Role.objects.all().filter(club=self.club).count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_all_members,after_all_members)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_banned_members_cannot_apply_to_same_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        before_all_members = Role.objects.all().filter(club=self.club).count()
        response = self.client.get(self.url)
        after_applicants = Role.objects.all().filter(club=self.club,club_role='APP').count()
        after_all_members = Role.objects.all().filter(club=self.club).count()
        self.assertEqual(before_applicants,after_applicants)
        self.assertEqual(before_all_members,after_all_members)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_apply_user_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
