from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import When
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from enum import Enum
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\w{3,}$',
                message='Username must consist of at least three alphanumericals'
                )
            ]
    )
    first_name = models.CharField(
        max_length=50,
        blank=False
    )
    last_name = models.CharField(
        max_length=50,
        blank=False
    )
    email = models.EmailField(
        unique=True,
        blank=False
    )
    bio = models.CharField(
        max_length=520,
        blank=True
    )

    class ChessExperience(models.IntegerChoices):
        BEGINNER = 1, _('Beginner')
        EXPERIENCED = 2, _('Experienced')
        INTERMEDIATE = 3, _('Intermediate')
        ADVANCED = 4, _('Advanced')
        EXPERT = 5, _('Expert')

    chess_experience_level = models.IntegerField(
        default=ChessExperience.BEGINNER,
        choices = ChessExperience.choices
    )

    def get_Chess_Experience(self):
        return self.ChessExperience(self.chess_experience_level).name.title()

    is_applicant = models.BooleanField(default = False)
    
    def toggle_applicant(user):
        if user.is_applicant == True:
            user.is_applicant = False
            user.save()
            return
        elif user.is_applicant == False:
            user.is_applicant = True
            user.save()

    is_member = models.BooleanField(default = False)

    def toggle_member(user):
        if user.is_member == True:
            user.is_member = False
            user.save()
            return
        elif user.is_member == False:
            user.is_applicant = False
            user.is_member = True
            user.save()


    is_officer = models.BooleanField(default = False)
    
    def toggle_officer(user):
        if user.is_officer == True:
            user.is_officer = False
            user.save()
            return
        elif user.is_officer == False:
            user.is_officer = True
            user.save()
    

    is_owner = models.BooleanField(default = False)

 
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    def mini_gravatar(self):
        "Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)


    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url
