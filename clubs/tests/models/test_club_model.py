"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Role,User,Club

class ClubModelTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = [

        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
        ]

    def setUp(self):
        self.club = Club.objects.get(club_name='Beatles')
        self.user = User.objects.get(username = 'johndoe@example.org')

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

    def test_toggle_member(self):
        applicant_user = User.objects.get(username='janedoe@example.org')
        self.club.club_members.add(applicant_user,through_defaults={'club_role':'APP'})
        self.assertEqual(self.club.get_club_role(applicant_user),'APP')
        self.club.toggle_member(applicant_user)
        self.assertEqual(self.club.get_club_role(applicant_user),'MEM')

    def test_transfer_ownership_must_promote_officers(self):
        owner_user = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(owner_user,through_defaults={'club_role':'OWN'})
        self.assertEqual(self.club.get_club_role(owner_user),'OWN')
        officer_user = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(officer_user,through_defaults={'club_role':'OFF'})
        self.assertEqual(self.club.get_club_role(officer_user),'OFF')
        self.club.transfer_ownership(owner_user,officer_user)
        self.assertEqual(self.club.get_club_role(officer_user),'OWN')
        self.assertEqual(self.club.get_club_role(owner_user),'OFF')

    def test_transfer_ownership_must_not_promote_non_officers(self):
        owner_user = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(owner_user,through_defaults={'club_role':'OWN'})
        self.assertEqual(self.club.get_club_role(owner_user),'OWN')
        member_user = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(member_user,through_defaults={'club_role':'MEM'})
        self.assertEqual(self.club.get_club_role(member_user),'MEM')
        self.club.transfer_ownership(owner_user,member_user)
        self.assertEqual(self.club.get_club_role(owner_user),'OWN')
        self.assertEqual(self.club.get_club_role(member_user),'MEM')

    def test_toggle_member(self):
        applicant_user = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(applicant_user,through_defaults={'club_role':'APP'})
        self.assertEqual(self.club.get_club_role(applicant_user),'APP')
        self.club.toggle_member(applicant_user)
        self.assertEqual(self.club.get_club_role(applicant_user),'MEM')


    def test_toggle_officer_on_non_applicants(self):
        member_user = User.objects.get(username='robertdoe@example.org')
        self.club.club_members.add(member_user,through_defaults={'club_role':'MEM'})
        self.assertEqual(self.club.get_club_role(member_user),'MEM')
        self.club.toggle_officer(member_user)
        self.assertEqual(self.club.get_club_role(member_user),'OFF')

    def test_toggle_officer_must_not_be_applicant(self):
        applicant_user = User.objects.get(username='bobdoe@example.org')
        self.club.club_members.add(applicant_user,through_defaults={'club_role':'APP'})
        self.assertEqual(self.club.get_club_role(applicant_user),'APP')
        self.club.toggle_officer(applicant_user)
        self.assertEqual(self.club.get_club_role(applicant_user),'APP')

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
