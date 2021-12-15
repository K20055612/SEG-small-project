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
@method_decorator(management_required,name='dispatch')
class MemberManagementListView(LoginRequiredMixin,ListView):
    model = User
    template_name = "member_management.html"
    context_object_name = 'members'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(MemberManagementListView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        context['club'] = self.club
        context['banned'] = self.club.get_banned_members()
        context['members'] = self.club.get_members()
        return context

@login_required
@club_exists
@user_in_club
@management_required
def promote_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    member = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'MEM')
    current_club.toggle_officer(member)
    return redirect('member_management', current_club.club_name)

@login_required
@club_exists
@user_in_club
@management_required
def ban_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    member = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'MEM')
    current_club.ban_member(member)
    return redirect('member_management', current_club.club_name)

@login_required
@club_exists
@user_in_club
@management_required
def unban_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    banned = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'BAN')
    current_club.unban_member(banned)
    return redirect('member_management', current_club.club_name)

@method_decorator(login_required,name='dispatch')
@method_decorator(club_exists,name='dispatch')
@method_decorator(owner_required,name='dispatch')
class OfficerListView(LoginRequiredMixin,ListView):
    model = User
    template_name = "officer_list.html"
    context_object_name = 'officers'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(OfficerListView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        context['club'] = self.club
        context['officers'] = self.club.get_officers()
        return context

@login_required
@club_exists
@user_in_club
@owner_required
def transfer_ownership(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    officer = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'OFF')
    current_club.transfer_ownership(request.user,officer)
    return redirect('officer_list', current_club.club_name)

@login_required
@club_exists
@user_in_club
@owner_required
def demote_officer(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    officer = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'OFF')
    current_club.toggle_member(officer)
    return redirect('officer_list', current_club.club_name)
