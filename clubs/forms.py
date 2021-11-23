from django import forms
from .models import User
from django.core.validators import RegexValidator
from .models import User

class LogInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
