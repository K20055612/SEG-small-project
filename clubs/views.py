from django.shortcuts import redirect, render
from .forms import SignUpForm
from .models import User
from django.contrib.auth import authenticate, login, logout


def home(request):
    return render(request, 'home.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})
