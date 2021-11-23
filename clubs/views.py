from django.shortcuts import redirect, render
from .forms import SignUpForm
from .models import User
from django.contrib.auth import authenticate, login, logout


def home(request):
    return render(request, 'home.html')

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
