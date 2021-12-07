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

def log_out(request):
    logout(request)
    return redirect('home')


@login_required
def feed(request):
    clubs= Club.objects.all()
    current_user= request.user
    user_applicant_clubs = Club.objects.all().filter(
        club_members__username=current_user.username,
        role__club_role='APP')
    user_clubs = Club.objects.all().filter(
        club_members__username=current_user.username).difference(user_applicant_clubs)
    return render(request,'feed.html', {'clubs':clubs, 'user_clubs':user_clubs, 'user_applicant_clubs':user_applicant_clubs})


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

@login_required
def create_club(request):
    if request.method =='POST':
        form = NewClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            club.club_members.add(request.user,through_defaults={'club_role':'OWN'})
            return redirect('feed')
    else:
        form = NewClubForm()
    return render(request,'new_club.html',{'form':form})


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

@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('feed')
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})


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
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('feed')

@login_required
@club_exists
def apply_to_club(request,club_name):
    try:
        club = Club.objects.get(club_name=club_name)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        try:
            club.get_club_role(request.user)
        except (ObjectDoesNotExist):
            club.club_members.add(request.user,through_defaults={'club_role':'APP'})
            club.save()
            return feed(request)
        else:
            return redirect('feed')

@login_required
@club_exists
@management_required
def applicants_list(request,club_name):
        current_club = Club.objects.get(club_name=club_name)
        applicants = current_club.get_applicants()
        return render(request,'applicants_list.html', {'applicants':applicants, 'current_club':current_club})

@login_required
@club_exists
@membership_required
def club_feed(request,club_name):
    is_officer = False
    is_owner = False
    current_club = Club.objects.get(club_name=club_name)
    club_role = current_club.get_club_role(request.user)
    members = current_club.get_members()
    number_of_applicants = current_club.get_applicants().count()
    if club_role == 'OWN':
        is_owner = True
    elif club_role == 'OFF':
        is_officer = True
    return render(request,'club_feed.html', {'club':current_club,'is_officer':is_officer,'is_owner':is_owner,'members':members,'number_of_applicants':number_of_applicants})

@login_required
@club_exists
def club_welcome(request,club_name):
    is_applicant = False
    is_member = False
    club = Club.objects.get(club_name=club_name)
    user = request.user
    try:
        club_role = club.get_club_role(user)
    except Role.DoesNotExist:
        return render(request,'club_welcome.html', {'club':club, 'user':user, 'is_applicant':is_applicant,'is_member':is_member})
    else:
        if club_role == 'APP':
            is_applicant = True
        elif club_role ==  'MEM' or club_role ==  'OWN' or club_role ==  'OFF':
            is_member = True
    return render(request,'club_welcome.html', {'club':club, 'user':user, 'is_applicant':is_applicant,'is_member':is_member})

@login_required
@club_exists
@management_required
def accept_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id)
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
            applicant = User.objects.get(id=user_id)
            current_club.remove_user_from_club(applicant)
        except ObjectDoesNotExist:
            return redirect('feed')
        else:
            return applicants_list(request,current_club.club_name)

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
        officer = User.objects.get(id=user_id)
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
        officer = User.objects.get(id=user_id)
        current_club.toggle_member(officer)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return officer_list(request,current_club.club_name)
