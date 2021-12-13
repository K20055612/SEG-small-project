"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User,Club,Role

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [

        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',


        ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')
        self.first_club = Club.objects.get(club_name='Beatles')
        self.first_club.club_members.add(self.user,through_defaults={'club_role':'OFF'})
        self.second_club = Club.objects.get(club_name='EliteChess')
        self.second_club.club_members.add(self.user,through_defaults={'club_role':'MEM'})
        self.third_club = Club.objects.get(club_name='ADCD')
        self.third_club.club_members.add(self.user,through_defaults={'club_role':'OWN'})


    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()


    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.last_name = User.objects.get(username='johndoe@example.org')
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()


    def test_email_must_not_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.username = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.username = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.username = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.username = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.username = 'johndoe@@example.org'
        self._assert_user_is_invalid()


    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    def test_chess_experience_level_must_not_be_less_than_1(self):
        self.user.chess_experience_level = 0
        self._assert_user_is_invalid()

    def test_chess_experience_level_must_not_be_greater_than_5(self):
        self.user.chess_experience_level = 6
        self._assert_user_is_invalid()

    def test_chess_experience_level_may_be_greater_or_equal_to_1_and_less_or_equal_to_5(self):
        self.user.chess_experience_level = 3
        self._assert_user_is_valid()

    def test_get_chess_experience_level(self):
        self.assertEqual(self.user.get_chess_experience(),'Beginner')

    def test_get_full_name(self):
        self.assertEqual(self.user.full_name(),'John Doe')

    def test_get_user_clubs(self):
        clubs = self.user.get_user_clubs()
        self.assertEqual(clubs.count(),3)
        
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
