from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User,Club,Role
from django.contrib import messages
from .forms import LogInForm,SignUpForm,UserForm,PasswordForm,NewClubForm
from django.contrib.auth.decorators import login_required
from .helpers import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.views import View
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

def home(request):
    return render(request, 'home.html')

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

"""log out redirect to home page"""
def log_out(request):
    logout(request)
    return redirect('home')

class FeedView(LoginRequiredMixin,ListView):
    model = Club
    template_name = "feed.html"
    context_object_name = 'clubs'

    def get_context_data(self,*args,**kwargs):
        context = super(FeedView,self).get_context_data(*args,**kwargs)
        context['user_clubs'] = self.request.user.get_user_clubs()
        context['user_applicant_clubs'] = self.request.user.get_applied_clubs()
        return context

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


"""only login user can create new club"""
class CreateClubView(LoginRequiredMixin,FormView):
    form_class = NewClubForm
    template_name = "new_club.html"
    #redirect_when_logged_in_url = settings

    def form_valid(self,form):
        self.object = form.save()
        self.object.club_members.add(self.request.user,through_defaults={'club_role':'OWN'})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('feed')

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

"""only if the user is login and club exists can user apply to the club"""
@login_required
@club_exists
def apply_to_club(request,club_name):
    is_banned = False
    try:
        club = Club.objects.get(club_name=club_name)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        try:
            role = club.get_club_role(request.user)
        except (ObjectDoesNotExist):
            club.club_members.add(request.user,through_defaults={'club_role':'APP'})
            club.save()
            return feed(request)
        else:
            return redirect('feed')

@method_decorator(club_exists,name='dispatch')
@method_decorator(management_required,name='dispatch')
class ApplicantListView(LoginRequiredMixin,ListView):
    model = User
    template_name = "applicants_list.html"
    context_object_name = 'users'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(ApplicantListView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        context['users'] = self.club.get_applicants()
        context['club'] = self.club
        return context

@method_decorator(club_exists,name='dispatch')
@method_decorator(membership_required,name='dispatch')
class ClubFeedView(LoginRequiredMixin,ListView):
    model = User
    template_name = "club_feed.html"
    context_object_data = 'members'

    def get_context_data(self,*args,**kwargs):
        context = super(ClubFeedView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        club_role = self.club.get_club_role(self.request.user)
        context['members'] = self.club.get_members()
        context['club'] = self.club
        context['management'] = self.club.get_management()
        is_officer = False
        is_owner = False
        if club_role == 'OWN':
            is_owner = True
        elif club_role == 'OFF':
            is_officer = True
        context['is_owner'] = is_owner
        context['is_officer'] = is_officer
        context['number_of_applicants'] = self.club.get_applicants().count()
        return context

@login_required
@club_exists
def club_welcome(request,club_name):
    is_applicant = False
    is_member = False
    is_banned = False
    club = Club.objects.get(club_name=club_name)
    user = request.user
    try:
        club_role = club.get_club_role(user)
    except Role.DoesNotExist:
        return render(request,'club_welcome.html', {'club':club, 'user':user, 'is_applicant':is_applicant,'is_member':is_member,'is_banned':is_banned})
    else:
        if club_role == 'APP':
            is_applicant = True
        elif club_role == 'BAN':
            is_banned = True
        elif club_role ==  'MEM' or club_role ==  'OWN' or club_role ==  'OFF':
            is_member = True
    return render(request,'club_welcome.html', {'club':club, 'user':user, 'is_applicant':is_applicant,'is_member':is_member, 'is_banned':is_banned})

@login_required
@club_exists
@management_required
def accept_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
            current_club.toggle_member(applicant)
        except (ObjectDoesNotExist):
            return redirect('feed')

        else:
            return applicants_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def reject_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
            current_club.remove_user_from_club(applicant)
        except ObjectDoesNotExist:
            return redirect('feed')
        else:
            return applicants_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def ban_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'MEM')
        current_club.ban_member(member)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return members_management_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def unban_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        banned = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'BAN')
        current_club.unban_member(banned)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return members_management_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def members_management_list(request,club_name):
    banned_is_empty = False
    member_is_empty = False
    current_club = Club.objects.get(club_name=club_name)
    members = current_club.get_members()
    banned = current_club.get_banned_members()
    if members.count() == 0:
        member_is_empty = True
    if banned.count() == 0:
        banned_is_empty = True
    return render(request,'member_management.html', {'banned':banned,'members':members, 'banned_is_empty':banned_is_empty,'member_is_empty':member_is_empty, 'current_club':current_club})

@login_required
@club_exists
@owner_required
def officer_list(request,club_name):
    current_club = Club.objects.get(club_name=club_name)
    officers = current_club.get_officers()
    return render(request,'officer_list.html', {'officers':officers, 'current_club':current_club})

@login_required
@club_exists
@owner_required
def transfer_ownership(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        officer = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'OFF')
        current_club.transfer_ownership(request.user,officer)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return officer_list(request,current_club.club_name)

@login_required
@club_exists
@owner_required
def demote_officer(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        officer = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'OFF')
        current_club.toggle_member(officer)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return officer_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def promote_member(request,club_name,user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'MEM')
        current_club.toggle_officer(member)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return members_management_list(request,current_club.club_name)

@login_required
@club_exists
@owner_required
def delete_club(request,club_name):
    current_club = Club.objects.get(club_name=club_name)
    current_club.delete()
    return feed(request)
