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

@method_decorator(club_exists_id,name='dispatch')
class ClubWelcomeView(LoginRequiredMixin,DetailView):
    model = Club
    template_name = 'club_welcome.html'
    context_object_name = "club"
    pk_url_kwarg = 'club_id'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        context = super(ClubWelcomeView,self).get_context_data(*args, **kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        user_role = None
        if club.is_user_in_club(self.request.user):
            club_role = club.get_club_role(self.request.user)
            if club_role == 'APP':
                user_role = 'APP'
            elif club_role == 'BAN':
                user_role = 'BAN'
            elif club_role ==  'MEM' or club_role ==  'OWN' or club_role ==  'OFF':
                user_role = 'MEM'
        context['club'] = club
        context['user'] = self.request.user
        context['user_role'] = user_role
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""
        try:
          return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('feed')

@login_required
@club_exists
@owner_required
def delete_club(request,club_name):
        current_club = Club.objects.get(club_name=club_name)
        current_club.delete()
        return redirect('feed')
"""only login user can create new club"""
class CreateClubView(LoginRequiredMixin,FormView):
    form_class = NewClubForm
    template_name = "new_club.html"

    def form_valid(self,form):
        self.object = form.save()
        self.object.club_members.add(self.request.user,through_defaults={'club_role':'OWN'})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('feed')
