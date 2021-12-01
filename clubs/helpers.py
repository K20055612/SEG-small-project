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

def management_required(view_function):
    def modified_view_function(request,club_name,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'OFF' or role.club_role == 'OWN':
                return view_function(request,club_name,*args,**kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    return modified_view_function

def owner_required(view_function):
    def modified_view_function(request,club_name,*args,**kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'OWN':
                return view_function(request,club_name,*args,**kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    return modified_view_function
