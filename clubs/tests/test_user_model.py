"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [

        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/member_user.json',
        'clubs/tests/fixtures/officer_user.json',
        'clubs/tests/fixtures/owner_user.json',
        'clubs/tests/fixtures/applicant_user.json'
        ]

    def setUp(self):
        self.user = User.objects.get(username='bobdoe')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = 'x' * 30
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = 'x' * 31
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = User.objects.get(username='janedoe')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_username_must_contain_only_alphanumericals(self):
        self.user.username = 'bob!doe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumericals(self):
        self.user.username = 'bo'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = 'bob0doe2'
        self._assert_user_is_valid()


    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe')
        self.user.first_name = User.objects.get(username='janedoe')
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
        second_user = User.objects.get(username='janedoe')
        self.user.last_name = User.objects.get(username='janedoe')
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()


    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(username='janedoe')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()


    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe')
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

    def test_is_applicant_cannot_be_blank(self):
        self.user.is_applicant = ''
        self._assert_user_is_invalid()

    def test_is_member_cannot_be_blank(self):
        self.user.is_member = ''
        self._assert_user_is_invalid()

    def test_is_officer_cannot_be_blank(self):
        self.user.is_officer = ''
        self._assert_user_is_invalid()

    def test_is_owner_cannot_be_blank(self):
        self.user.is_owner = ''
        self._assert_user_is_invalid()

    def test_owner_must_be_officer(self):
        owner_user = User.objects.get(username='janedoe')
        before = owner_user.is_officer
        owner_user.toggle_officer()
        after = owner_user.is_officer
        self.assertEqual(before,after)
        
    def test_visitor_must_not_have_a_role_in_club(self):
        visitor_user = User.objects.get(username='josedoe')
        self.assertFalse(visitor_user.is_applicant)
        self.assertFalse(visitor_user.is_member)
        self.assertFalse(visitor_user.is_officer)
        self.assertFalse(visitor_user.is_owner)
        self._assert_user_is_valid()

    def test_owner_must_be_officer(self):
        owner_user = User.objects.get(username='janedoe')
        self.assertTrue(owner_user.is_officer)
        self._assert_user_is_valid()

    def test_owner_must_be_member(self):
        owner_user = User.objects.get(username='janedoe')
        before = owner_user.is_member
        owner_user.toggle_officer()
        after = owner_user.is_officer
        self.assertEqual(before,after)
        self.assertTrue(owner_user.is_member)
        self._assert_user_is_valid()

    def test_officer_must_be_member(self):
        officer_user = User.objects.get(username='johndoe')
        before = officer_user.is_member
        officer_user.toggle_member()
        after = officer_user.is_member
        self.assertEqual(before,after)
        self.assertTrue(officer_user.is_member)
        self._assert_user_is_valid()

    def test_applicant_must_not_be_member(self):
        applicant_user = User.objects.get(username='alicedoe')
        self.assertFalse(applicant_user.is_member)
        self._assert_user_is_valid()

    def test_applicant_must_not_be_officer(self):
        applicant_user = User.objects.get(username='alicedoe')
        self.assertFalse(applicant_user.is_officer)
        self._assert_user_is_valid()

    def test_applicant_must_not_be_owner(self):
        applicant_user = User.objects.get(username='alicedoe')
        self.assertFalse(applicant_user.is_owner)
        self._assert_user_is_valid()

    def test_member_must_not_be_officer(self):
        applicant_user = User.objects.get(username='bobdoe')
        self.assertFalse(applicant_user.is_officer)
        self._assert_user_is_valid()

    def test_member_must_not_be_owner(self):
        applicant_user = User.objects.get(username='bobdoe')
        self.assertFalse(applicant_user.is_owner)
        self._assert_user_is_valid()

    def test_officer_must_not_be_owner(self):
        applicant_user = User.objects.get(username='johndoe')
        self.assertFalse(applicant_user.is_owner)
        self._assert_user_is_valid()
        member_user = User.objects.get(username='bobdoe')
        self.assertFalse(member_user.is_officer)
        self._assert_user_is_valid()

    def test_member_must_not_be_applicant(self):
        member_user = User.objects.get(username='bobdoe')
        self.assertFalse(member_user.is_applicant)
        self._assert_user_is_valid()

    def test_officer_must_not_be_applicant(self):
        officer_user = User.objects.get(username='johndoe')
        self.assertFalse(officer_user.is_applicant)
        self._assert_user_is_valid()

    def test_owner_must_not_be_applicant(self):
        owner_user = User.objects.get(username='janedoe')
        self.assertFalse(owner_user.is_applicant)
        self._assert_user_is_valid()

    def test_member_must_not_be_owner(self):
        member_user = User.objects.get(username='bobdoe')
        self.assertFalse(member_user.is_owner)
        self._assert_user_is_valid()

    def test_officer_must_not_be_owner(self):
        officer_user = User.objects.get(username='johndoe')
        self.assertFalse(officer_user.is_owner)
        self._assert_user_is_valid()

    def test_toggle_applicant(self):
        visitor_user = User.objects.get(username='josedoe')
        self.assertFalse(visitor_user.is_applicant)
        visitor_user.toggle_applicant()
        self.assertTrue(visitor_user.is_applicant)
        applicant_user = User.objects.get(username='alicedoe')
        self.assertTrue(applicant_user.is_applicant)
        applicant_user.toggle_applicant()
        self.assertFalse(applicant_user.is_applicant)

    def test_toggle_member(self):
        applicant_user = User.objects.get(username='alicedoe')
        self.assertFalse(applicant_user.is_member)
        self.assertTrue(applicant_user.is_applicant)
        applicant_user.toggle_member()
        self.assertTrue(applicant_user.is_member)
        self.assertFalse(applicant_user.is_applicant)
        member_user = User.objects.get(username='bobdoe')
        self.assertTrue(member_user.is_member)
        member_user.toggle_member()
        self.assertFalse(member_user.is_member)

    def test_toggle_officer(self):
        member_user = User.objects.get(username='bobdoe')
        self.assertFalse(member_user.is_officer)
        member_user.toggle_officer()
        self.assertTrue(member_user.is_officer)
        officer_user = User.objects.get(username='johndoe')
        self.assertTrue(member_user.is_officer)
        officer_user.toggle_officer()
        self.assertFalse(officer_user.is_officer)

    # def test_toggle_owner(self):
    #     applicant_user = User.objects.get(username='alicedoe')
    #     self.assertFalse(applicant_user.is_member)
    #     applicant_user.toggle_member()
    #     self.assertTrue(applicant_user.is_member)
    #     member_user = User.objects.get(username='bobdoe')
    #     self.assertTrue(member_user.is_member)
    #     member_user.toggle_member()
    #     self.assertFalse(member_user.is_member)

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
