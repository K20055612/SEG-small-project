"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from clubs.forms import UserForm
from clubs.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'first_name':'Jane',
            'last_name' : 'Doe',
            'username' : 'janedoe@example.org',
            'bio' : 'My bio',
            'new_password':'Password123',
            'password_confirmation': 'Password123',
            'chess_experience_level': '1'
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        email_field = form.fields['username']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('chess_experience_level',form.fields)

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'bademail'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='johndoe@example.org')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        user = User.objects.get(username = 'janedoe@example.org')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.username, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_experience_level,1)
