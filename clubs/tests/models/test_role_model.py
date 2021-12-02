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
