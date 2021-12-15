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

@method_decorator(login_required,name='dispatch')
@method_decorator(club_exists,name='dispatch')
@method_decorator(membership_required,name='dispatch')

class ClubFeedView(LoginRequiredMixin,ListView):
    model = User
    template_name = "club_feed.html"
    context_object_data = 'members'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(ClubFeedView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        user_role = self.club.get_club_role(self.request.user)
        context['members'] = self.club.get_members()
        context['club'] = self.club
        context['management'] = self.club.get_management()
        context['user_role'] = user_role
        context['number_of_applicants'] = self.club.get_applicants().count()
        return context

@login_required
@membership_required
def search_member(request,club_name):
    current_club = Club.objects.get(club_name=club_name)
    members = current_club.get_all_users_in_club()
    member_name = request.GET.get('member_name')
    if member_name == '':
        member_name = 'None'
    queryset = members.annotate(search_name=Concat('first_name', Value(' '), 'last_name'))
    search_results = queryset.filter(search_name__contains=member_name)

    return render(request,'search_member.html', {'club':current_club,'members':search_results})
