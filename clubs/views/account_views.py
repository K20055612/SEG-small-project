from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from clubs.models import User,Club,Role
from django.contrib import messages
from clubs.forms import LogInForm,SignUpForm,UserForm,PasswordForm,NewClubForm
from django.contrib.auth.decorators import login_required
from clubs.helpers import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.views import View
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from .mixins import LoginProhibitedMixin


class SignUpView(LoginProhibitedMixin, FormView):
    """View that signs up user."""
    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('feed')
