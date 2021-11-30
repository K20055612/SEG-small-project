"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Club

class ClubModelTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = [

        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',

        ]

    def setUp(self):
        self.club = Club.objects.get(club_name='Beatles')


    def test_valid_club(self):
        self._assert_club_is_valid()

    def test_club_name_cannot_be_blank(self):
        self.club.club_name = ''
        self._assert_club_is_invalid()

    def test_club_name_can_be_50_characters_long(self):
        self.club.club_name = 'x' * 50
        self._assert_club_is_valid()

    def test_club_name_cannot_be_over_50_characters_long(self):
        self.club.club_name = 'x' * 51
        self._assert_club_is_invalid()

    def test_club_name_must_be_unique(self):
        second_club = Club.objects.get(club_name='ADCD')
        self.club.club_name = second_club.club_name
        self._assert_club_is_invalid()

    def test_club_name_must_contain_only_alphanumericals(self):
        self.club.club_name = 'Bea!les'
        self._assert_club_is_invalid()

    def test_club_name_may_contain_numbers(self):
        self.club.club_name = 'Beatles2'
        self._assert_club_is_valid()

    def test_club_location_cannot_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_club_location_can_be_100_characters_long(self):
        self.club.location = 'x' * 100
        self._assert_club_is_valid()

    def test_club_location_cannot_be_over_100_characters_long(self):
        self.club.location = 'x' * 101
        self._assert_club_is_invalid()

    def test_location_may_not_be_unique(self):
        second_club = Club.objects.get(club_name='ADCD')
        self.club.location = second_club.location
        self._assert_club_is_valid()

    def test_club_location_may_contain_numbers(self):
        self.club.location = 'London, Street 2'
        self._assert_club_is_valid()

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()