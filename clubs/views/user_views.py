from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from clubs.models import User
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from clubs.helpers import user_exists
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.urls import reverse

@method_decorator(user_exists,name='dispatch')
class ShowUserView(LoginRequiredMixin, DetailView):
    """View that shows individual user details."""

    model = User
    template_name = 'show_user.html'
    context_object_name = "user"
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        current_user_clubs = self.request.user.get_user_clubs()
        selected_user_clubs = user.get_user_clubs()
        communal_clubs = current_user_clubs.intersection(selected_user_clubs)

        context = super().get_context_data(object_list=communal_clubs, **kwargs)
        context['user'] = user
        context['communal_clubs'] = context['object_list']
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('feed')
