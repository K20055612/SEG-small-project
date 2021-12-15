from django.shortcuts import render, redirect
from clubs.models import User,Club,Role
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from clubs.helpers import *
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

@method_decorator(login_required,name='dispatch')
@method_decorator(club_exists,name='dispatch')
@method_decorator(management_required,name='dispatch')
class ApplicantListView(LoginRequiredMixin,ListView):

    model = User
    template_name = "applicants_list.html"
    context_object_name = 'applicants'


    def post(self,*args,**kwargs):
        return super().get(*args,**kwargs)

    def get_context_data(self,*args,**kwargs):
        context = super(ApplicantListView,self).get_context_data(*args,**kwargs)
        self.club = Club.objects.get(club_name=self.kwargs['club_name'])
        context['club'] = self.club
        context['applicants'] = self.club.get_applicants()
        return context

@login_required
@user_in_club
@management_required
def accept_applicant(request,club_name,user_id):

    current_club = Club.objects.get(club_name=club_name)
    applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
    current_club.toggle_member(applicant)
    if request.method == 'POST':
        messages.add_message(request, messages.SUCCESS, f'{applicant.full_name()} has become a member of the club.')
    return redirect('applicants_list', current_club.club_name)

@login_required
@club_exists
@user_in_club
@management_required
def reject_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
        current_club.remove_user_from_club(applicant)
        if request.method == 'POST':
            messages.add_message(request, messages.DANGER, f'{applicant.full_name()} has been rejected.')
        return redirect('applicants_list', current_club.club_name)
        return redirect('applicants_list', current_club.club_name)

@login_required
@club_exists
def apply_to_club(request,club_name):
    if request.method == 'POST':
        messages.add_message(request, messages.SUCCESS, f'Application for {club_name} sent successfully. Hang tight while a club officer reviews your application.')
    club = Club.objects.get(club_name=club_name)
    try:
        role = club.get_club_role(request.user)
    except (ObjectDoesNotExist):
            club.club_members.add(request.user,through_defaults={'club_role':'APP'})
            club.save()
            return redirect('club_welcome',club.id)
    else:
            return redirect('feed')

@login_required
@user_in_club
@club_exists
def withdraw_application(request, club_name, user_id):
    club = Club.objects.get(club_name = club_name)
    try:
        applicant = User.objects.get(id=user_id,club__club_name = club.club_name, role__club_role = 'APP')
        club.remove_user_from_club(applicant)
        club.save()
    except ObjectDoesNotExist:
        return redirect('feed')
    if request.method == 'POST':
        messages.add_message(request, messages.WARNING, f'Withdrawal from {club_name} completed successfully')
    return redirect('feed')