from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User
from django.contrib import messages
from .forms import LogInForm
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited


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
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('profile')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})

def log_out(request):
    logout(request)
    return redirect('home')

def profile(request):
    return render(request, 'profile.html')

#@login_required
def applicants_list(request):
    applicants = User.objects.all().filter(is_member=False)
    return render(request,'applicants_list.html', {'applicants':applicants})
