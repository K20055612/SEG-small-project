"""system URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('log_out/', views.log_out, name='log_out'),
    path('user/<int:user_id>/', views.ShowUserView.as_view(), name='show_user'),
    path('club/<str:club_name>/feed/', views.ClubFeedView.as_view() ,name='club_feed'),
    path('club/<str:club_name>/', views.club_welcome ,name='club_welcome'),
    path('club/<str:club_name>/applicants/accept/<int:user_id>/', views.accept_applicant,name='accept_applicant'),
    path('club/<str:club_name>/applicants/reject/<int:user_id>/', views.reject_applicant,name='reject_applicant'),
    path('club/<str:club_name>/member_management/ban/<int:user_id>/', views.ban_member,name='ban_member'),
    path('club/<str:club_name>/member_management/unban/<int:user_id>/', views.unban_member,name='unban_member'),
    path('club/<str:club_name>/member_management/', views.members_management_list,name='member_management'),
    path('club/<str:club_name>/member_management/promote_member/<int:user_id>/', views.promote_member,name='promote_member'),
    path('club/<str:club_name>/applicants/',views.ApplicantListView.as_view(),name='applicants_list'),
    path('club/<str:club_name>/officer_management/',views.officer_list,name='officer_list'),
    path('club/<str:club_name>/officer_management/new_owner/<int:user_id>/', views.transfer_ownership,name='transfer_ownership'),
    path('club/<str:club_name>/officer_management/demote_officer/<int:user_id>/', views.demote_officer,name='demote_officer'),
    path('apply/<str:club_name>/', views.apply_to_club,name='apply_to_club'),
    path('create_club/', views.CreateClubView.as_view(),name='create_club'),
    path('club/<str:club_name>/delete/', views.delete_club, name = 'delete_club'),

]
