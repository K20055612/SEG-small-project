from django.shortcuts import render
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

#@login_required
def applicants_list(request):
    applicants = User.objects.all().filter(is_member=False)
    return render(request,'applicants_list.html', {'applicants':applicants})
