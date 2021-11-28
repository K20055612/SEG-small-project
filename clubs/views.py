from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User
from django.contrib import messages
from .forms import LogInForm,SignUpForm,UserForm
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
            redirect_url = request.POST.get('next') or 'feed'
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('feed')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form , 'next':next})


def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def feed(request):
    return render(request, 'feed.html')

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
            return redirect('profile')
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
            return redirect('feed')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})

@login_required
def applicants_list(request):
    applicants = User.objects.all().filter(is_applicant=True)
    return render(request,'applicants_list.html', {'applicants':applicants})

@login_required
def member_list(request):
    members = User.objects.all().filter(is_member=True)
    return render(request,'member_list.html', {'members':members})

@login_required
def accept_applicant(request,user_id):
        try:
            applicant = User.objects.get(id=user_id)
            applicant.toggle_member()
            applicant.save()
        except ObjectDoesNotExist:
            return redirect('applicants_list')

        else:
            applicants = User.objects.all().filter(is_applicant=True)
            return render(request,'applicants_list.html', {'applicants':applicants})


@login_required
def reject_applicant(request,user_id):
        try:
            applicant = User.objects.get(id=user_id)
            applicant.toggle_applicant()
            applicant.save()
        except ObjectDoesNotExist:
            return redirect('applicants_list')
        else:
            applicants = User.objects.all().filter(is_applicant=True)
            return render(request,'applicants_list.html', {'applicants':applicants})
