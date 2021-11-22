from django.shortcuts import render
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

#@login_required
def main_officer_feed(request):
    applicants = User.objects.all().filter(is_member=False)
    members = User.objects.all().filter(is_member=True, is_officer=False, is_owner=False)
    return render(request,'officer_feed.html', {'applicants':applicants ,'members':members})
