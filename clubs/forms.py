from django import forms
from django.core.validators import RegexValidator
from .models import User,Club
from django.contrib.auth import authenticate

class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        labels = {
        "username": "Email:"}
        fields = ['first_name', 'last_name','username','bio','chess_experience_level']
        widgets = { 'bio': forms.Textarea() }



    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            username=self.cleaned_data.get('username'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            chess_experience_level = self.cleaned_data.get('chess_experience_level'),
        )
        return user


class LogInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user

class NewClubForm(forms.ModelForm):
    class Meta:

        model = Club
        fields = ['club_name', 'location','description']
        widgets = { 'description': forms.Textarea() }

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()

    def save(self):
        """Create a new club."""
        super().save(commit=False)
        club = Club.objects.create(
            club_name=self.cleaned_data.get('club_name'),
            location=self.cleaned_data.get('location'),
            description=self.cleaned_data.get('description'),
        )
        return club

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""
        model = User
        labels = {
        "username": "Email:"}
        fields = ['first_name', 'last_name','username', 'bio', 'chess_experience_level']
        widgets = { 'bio': forms.Textarea() }

class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')
