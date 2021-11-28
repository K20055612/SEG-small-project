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
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('feed/', views.feed, name='feed'),
    path('profile/', views.profile, name='profile'),
    path('password/', views.password, name='password'),
    path('log_out/', views.log_out, name='log_out'),
    path('applicants/', views.applicants_list, name='applicants_list'),
    path('members/', views.member_list, name='member_list'),
    path('accept/<int:user_id>/', views.accept_applicant, name='accept_applicant'),
    path('reject/<int:user_id>/', views.reject_applicant, name='reject_applicant'),
]
