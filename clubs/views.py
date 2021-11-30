from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User,Club,Role
from django.contrib import messages
from .forms import LogInForm,SignUpForm,UserForm,PasswordForm
from django.contrib.auth.decorators import login_required
from .helpers import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password


def home(request):
    return render(request, 'home.html')

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    redirect_url = request.POST.get('next') or 'feed'
                    return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form , 'next':next})

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def feed(request):
    clubs= Club.objects.all()

    current_user= request.user

    user_clubs = Club.objects.all().filter(
    club_members__username=current_user.username)

    return render(request,'feed.html', {'clubs':clubs, 'user_clubs':user_clubs})

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('profile')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})

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

@login_required
@management_login_required_applicant_list
def applicants_list(request,club_name):
        current_club = Club.objects.get(club_name=club_name)
        applicants = User.objects.all().filter(
        club__club_name=current_club.club_name,
        role__club_role='APP')
        return render(request,'applicants_list.html', {'applicants':applicants, 'current_club':current_club})

@login_required
def member_list(request,club_name):
    try:
        current_club = Club.objects.get(club_name=club_name)
        members = User.objects.all().filter(
        club__club_name=current_club.club_name,
        role__club_role='MEM')
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return render(request,'member_list.html', {'members':members, 'current_club':current_club})

@login_required
@member_required
def club_feed(request,club_name):
    club = Club.objects.get(club_name=club_name)
    user = request.user
    members = User.objects.all().filter(
        club__club_name=club_name,
        role__club_role='MEM')

    is_officer = False
    try:
        role = user.role_set.get(club=club)
        is_officer=role.club_role == 'OFF'
    except ObjectDoesNotExist:
        is_officer = False

    return render(request,'club_feed.html', {'club':club, 'user':user, 'members':members, 'is_officer':is_officer})

@login_required
def club_welcome(request,club_name):
    club = Club.objects.get(club_name=club_name)
    user = request.user

    is_applicant = False
    try:
        role = user.role_set.get(club=club)
        is_applicant=role.club_role == 'APP'
    except ObjectDoesNotExist:
        is_applicant = False

    return render(request,'club_welcome.html', {'club':club, 'user':user, 'is_applicant':is_applicant})

@login_required
@management_login_required_accept_reject
def accept_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=current_club.club_name,
            role__club_role='APP'
            )
            role = Role.objects.get(user=applicant,club=current_club,club_role='APP')
            role.toggle_member()
        except (ObjectDoesNotExist):
            return redirect('applicants_list', club_name=current_club.club_name)

        else:
            return applicants_list(request,current_club.club_name)

@login_required
@management_login_required_accept_reject
def reject_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=current_club.club_name,
            role__club_role='APP'
            )
            Role.objects.get(user=applicant,club=current_club,club_role='APP').delete()

        except ObjectDoesNotExist:
            return redirect('applicants_list', club_name=current_club.club_name)
        else:
            return applicants_list(request,current_club.club_name)
