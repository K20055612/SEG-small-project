"""Tests of the transfer_ownership view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Club,Role
from clubs.tests.helpers import LogInTester,reverse_with_next


class AcceptApplicantViewTestCase(TestCase,LogInTester):
    """Tests of the accept_applicant view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.applicant = User.objects.get(username='janedoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.club.club_members.add(self.applicant,through_defaults={'club_role':'APP'})
        self.url = reverse('accept_applicant',kwargs={'club_name': self.club.club_name,'user_id':self.applicant.id})

    def test_accept_applicant_url(self):
        self.assertEqual(self.url,f'/applicants/{self.club.club_name}/accept/{self.applicant.id}/')
