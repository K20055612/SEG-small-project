"""Unit tests of create club form."""
from django.test import TestCase
from clubs.models import Club
from clubs.forms import NewClubForm
from django import forms
from django.contrib.auth.hashers import check_password

class CreateClubFormTestCase(TestCase):
    """Unit tests of create club form."""

    def setUp(self):
        self.form_input = {
            'club_name':'Genius club',
            'location' : 'London',
            'description' : 'Best club in town!',
            }

    def test_valid_sign_up_form(self):
        form=NewClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = NewClubForm()
        self.assertIn('club_name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_form_must_save_correctly(self):
        form = NewClubForm(data = self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        club = Club.objects.get(club_name = 'Genius club')
        self.assertEqual(club.club_name, 'Genius club')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'Best club in town!')

    def test_form_uses_model_validation(self):
        self.form_input['club_name'] = 'clu'
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
