"""Unit tests of create club view."""
from django.test import TestCase
from clubs.models import Club,User,Role
from clubs.forms import NewClubForm
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next


class CreateClubViewTestCase(TestCase,LogInTester):
    """Unit tests of create club view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'club_name':'Genius club',
            'location' : 'London',
            'description' : 'Best club in town!',
            }
        self.url = reverse('create_club')
        self.user = User.objects.get(username='johndoe@example.org')

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/' )

    def test_get_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewClubForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['club_name'] = 'clu'
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewClubForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)
        self.assertTemplateUsed(response, 'feed.html')
        club = Club.objects.get(club_name = 'Genius club')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'Best club in town!')
        role = club.get_club_role(self.user)
        self.assertEqual(role,'OWN')

    def test_get_create_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_create_club_redirects_when_not_logged_in(self):
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
