"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from clubs.forms import SignUpForm
from django.urls import reverse
from clubs.models import User
from .helper import LogInTester


class SignUpViewTestCase(TestCase, LogInTester):
    """"Tests of the sign up view."""
    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name':'Jane',
            'last_name' : 'Doe',
            'username':'@jandoe',
            'email' : 'janedoe@example.com',
            'bio' : 'Hi, I am Jane.",
            'new_password':'Password1234',
            'password_confirmation': 'Password1234'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/' )

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['username'] = 'John'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)
        self.assertTemplateUsed(response, 'feed.html')
        user = User.objects.get(username = '@jandoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.bio, 'Hi, I am Jane.')
        is_password_correct = check_password('Password1234', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())
