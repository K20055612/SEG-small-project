"""Tests of the accept_user view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from .helpers import LogInTester,reverse_with_next


class AcceptUserViewTestCase(TestCase):
    """Tests of the accept_user view."""

    fixtures = ['clubs/tests/fixtures/applicant_user.json',
                'clubs/tests/fixtures/officer_user.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.applicant = User.objects.get(username='alicedoe')
        self.url = reverse('accept_applicant', kwargs={'user_id': self.applicant.id})

    def test_accept_applicant_url(self):
        self.assertEqual(self.url,f'/accept/{self.applicant.id}/')

    def test_accept_applicant_with_valid_id(self):
        self.client.login(username=self.user.email,password='Password123')
        before = User.objects.all().filter(is_applicant=True).count()
        response = self.client.get(self.url)
        after =  User.objects.all().filter(is_applicant=True).count()
        self.assertEqual(before,after+1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertNotContains(response, "Alice Doe")
        self.assertNotContains(response, "alicedoe")

    def test_accept_applicant_with_invalid_id(self):
        self.client.login(username=self.user.email, password='Password123')
        before = User.objects.all().filter(is_applicant=True).count()
        url = reverse('accept_applicant', kwargs={'user_id': self.user.id+9999})
        after = User.objects.all().filter(is_applicant=True).count()
        self.assertEqual(before,after)
        self.assertFalse(self.user.is_applicant)
        response = self.client.get(url, follow=True)
        response_url = reverse('applicants_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'applicants_list.html')

    def test_accept_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
