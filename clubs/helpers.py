from django.shortcuts import redirect
from django.conf import settings
from .models import User,Club,Role
from django.core.exceptions import ObjectDoesNotExist

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function
    
"""check whether the user is an officer or an owner"""
def management_required(view_function):
    def modified_view_function(request,club_name,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = club.get_club_role(request.user)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role == 'OFF' or role == 'OWN':
                return view_function(request,club_name,*args,**kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    return modified_view_function

"""check whether the user is an owner"""
def owner_required(view_function):
    def modified_view_function(request,club_name,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = club.get_club_role(request.user)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role == 'OWN':
                return view_function(request,club_name,*args,**kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    return modified_view_function

"""check whether the user is a member"""
def membership_required(view_function):
        def modified_view_function(request,club_name,*args,**kwargs):
            try:
                club = Club.objects.get(club_name=club_name)
                role = request.user.role_set.get(club=club)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                if role.club_role == 'MEM' or role.club_role == 'OFF' or role.club_role == 'OWN':
                    return view_function(request,club_name,*args,**kwargs)
                else:
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        return modified_view_function

"""check whether the club exists"""
def club_exists(view_function):
    def modified_view_function(request,club_name,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request,club_name,*args,**kwargs)
    return modified_view_function

def club_exists_id(view_function):
    def modified_view_function(request,club_id,*args,**kwargs):
        try:
            club = Club.objects.get(id=club_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request,club_id,*args,**kwargs)
    return modified_view_function

def user_exists(view_function):
    def modified_view_function(request,user_id,*args,**kwargs):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request,user_id,*args,**kwargs)
    return modified_view_function

def user_in_club(view_function):
    def modified_view_function(request,club_name,user_id,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            user = User.objects.get(id=user_id)
            role = club.get_club_role(user)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request,club_name,user_id,*args,**kwargs)
    return modified_view_function
