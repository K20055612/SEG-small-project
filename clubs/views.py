from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User,Club,Role
from django.contrib import messages
from .forms import LogInForm,SignUpForm
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    return render(request, 'home.html')


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            redirect_url = request.POST.get('next') or 'profile'
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('profile')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form , 'next':next})


def log_out(request):
    logout(request)
    return redirect('home')

def profile(request):
    return render(request, 'profile.html')

def login_prohibited(view_function):
    def modified_view_funtion(request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_function(request)
    return modified_view_funtion

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

#@login_required
def applicants_list(request,club_name):
    currentClub = Club.objects.get(club_name=club_name)
    applicants = User.objects.all().filter(
    club__club_name=currentClub.club_name,
    role__club_role='APP'
    )
    return render(request,'applicants_list.html', {'applicants':applicants, 'currentClub':currentClub})

#@login_required
def accept_applicant(request,club_name,user_id):
        currentClub = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=currentClub.club_name,
            role__club_role='APP'
            )
            role = Role.objects.get(user=applicant,club=currentClub,club_role='APP')
            role.toggle_member()
        except (ObjectDoesNotExist):
            return redirect('applicants_list')

        else:
            return applicants_list(request,club_name)


#@login_required
def reject_applicant(request,club_name,user_id):
        currentClub = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=currentClub.club_name,
            role__club_role='APP'
            )
            Role.objects.get(user=applicant,club=currentClub,club_role='APP').delete()
        except ObjectDoesNotExist:
            return redirect('applicants_list')
        else:
            return applicants_list(request,club_name)
