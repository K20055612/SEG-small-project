from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from clubs.models import User,Club
from django.views import View
from django.views.generic import ListView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


class FeedView(LoginRequiredMixin,ListView):
    """View that displays feed information such as a user's clubs and their applications"""
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
