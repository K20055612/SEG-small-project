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

    user_applicant_clubs = Club.objects.all().filter(
        club_members__username=current_user.username,
        role__club_role='APP')

    user_clubs = Club.objects.all().filter(
        club_members__username=current_user.username).difference(user_applicant_clubs)

    return render(request,'feed.html', {'clubs':clubs, 'user_clubs':user_clubs, 'user_applicant_clubs':user_applicant_clubs})

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
            return feed(request)
        else:
            return redirect('feed')

@login_required
@management_required
def applicants_list(request,club_name):
        current_club = Club.objects.get(club_name=club_name)
        applicants = current_club.get_applicants()
        return render(request,'applicants_list.html', {'applicants':applicants, 'current_club':current_club})

@login_required
<<<<<<< HEAD
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
=======
@membership_required
def member_list(request,club_name):
    try:
        current_club = Club.objects.get(club_name=club_name)
        members = current_club.get_members()
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return render(request,'member_list.html', {'members':members, 'current_club':current_club})
>>>>>>> apply-to-club

@login_required
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
@owner_required
def officer_list(request,club_name):
    current_club = Club.objects.get(club_name=club_name)
    officers = current_club.get_officers()
    return render(request,'officer_list.html', {'officers':officers, 'current_club':current_club})

@login_required
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
