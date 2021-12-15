from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from clubs.models import User,Club,Role
from django.contrib import messages
from clubs.forms import LogInForm,SignUpForm,UserForm,PasswordForm,NewClubForm
from django.contrib.auth.decorators import login_required
from clubs.helpers import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.views import View
from django.views.generic import ListView
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
from django.db.models import CharField, Value
from django.db.models.functions import Concat

class FeedView(LoginRequiredMixin,ListView):
    model = Club
    template_name = "feed.html"
    context_object_name = 'clubs'

    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(FeedView,self).get_context_data(*args,**kwargs)
        context['user_clubs'] = self.request.user.get_user_clubs()
        context['user_applicant_clubs'] = self.request.user.get_applied_clubs()
        return context
