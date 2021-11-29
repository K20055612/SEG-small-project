"""Unit tests for the Member model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Role,Club,User

class RoleModelTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.club = Club.objects.get(club_name='Beatles')
        self.role = Role(user = self.user, club = self.club, club_role = 'MEM')


    def test_valid_role(self):
        self._assert_role_is_valid()

    def test_user_may_not_be_blank(self):
        self.role.user = None
        self._assert_role_is_invalid()

    def test_club_may_not_be_blank(self):
        self.role.club = None
        self._assert_role_is_invalid()

    def test_toggle_member(self):
        applicant_user = User.objects.get(username='janedoe@example.org')
        janerole = Role(user = applicant_user, club=self.club,club_role='OFF')
        self.assertEqual(janerole.club_role,'OFF')
        janerole.toggle_member()
        self.assertEqual(janerole.club_role,'MEM')

    def test_toggle_officer(self):
        self.assertEqual(self.role.club_role,'MEM')
        self.role.toggle_officer()
        self.assertEqual(self.role.club_role,'OFF')


    def test_transfer_ownership_must_promote_officers(self):
        owner_user = User.objects.get(username='robertdoe@example.org')
        owner_role = Role(user = owner_user, club=self.club,club_role='OWN')
        self.assertEqual(owner_role.club_role,'OWN')
        officer_user = User.objects.get(username='bobdoe@example.org')
        officer_role = Role(user = officer_user, club=self.club,club_role='OFF')
        self.assertEqual(officer_role.club_role,'OFF')
        owner_role.transfer_ownership(officer_role)
        self.assertEqual(officer_role.club_role,'OWN')
        self.assertEqual(owner_role.club_role,'OFF')


    def test_transfer_ownership_must_not_promote_non_officers(self):
        owner_user = User.objects.get(username='robertdoe@example.org')
        owner_role = Role(user = owner_user, club=self.club,club_role='OWN')
        self.assertEqual(owner_role.club_role,'OWN')
        self.assertEqual(self.role.club_role,'MEM')
        owner_role.transfer_ownership(self.role)
        self.assertEqual(owner_role.club_role,'OWN')
        self.assertEqual(self.role.club_role,'MEM')

    def test_toggle_member(self):
        applicant_user = User.objects.get(username='bobdoe@example.org')
        applicant_role = Role(user = applicant_user, club=self.club,club_role='APP')
        self.assertEqual(applicant_role.club_role,'APP')
        applicant_role.toggle_member()
        self.assertEqual(applicant_role.club_role,'MEM')


    def test_toggle_officer_on_non_applicants(self):
        self.assertEqual(self.role.club_role,'MEM')
        self.role.toggle_officer()
        self.assertEqual(self.role.club_role,'OFF')


    def test_toggle_officer_must_not_be_applicant(self):
        applicant_user = User.objects.get(username='bobdoe@example.org')
        applicant_role = Role(user = applicant_user, club=self.club,club_role='APP')
        self.assertEqual(applicant_role.club_role,'APP')
        applicant_role.toggle_officer()
        self.assertEqual(applicant_role.club_role,'APP')

    def test_get_club_role(self):
        self.assertEqual(self.role.get_club_role(),'Member')

    def _assert_role_is_valid(self):
        try:
            self.role.full_clean()
        except (ValidationError):
            self.fail('Test role should be valid')

    def _assert_role_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.role.full_clean()
