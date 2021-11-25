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


class Club(models.Model):
    club_name = models.CharField(
    max_length=50,
    blank=False
    )
    location = models.CharField(
        max_length=100,
        blank=False
        )

    description = models.CharField(
        max_length=520,
        blank=False
        )

    club_members = models.ManyToManyField(User,through='UserRoles')

class UserRoles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)


    class Roles(models.TextChoices):
        APPLICANT = 'APP', _('Applicant')
        MEMBER = 'MEM', _('Member')
        OFFICER = 'OFF', _('Officer')
        OWNER = 'OWN', _('Owner')

    club_role = models.CharField(
        max_length = 3,
        choices = Roles.choices,
        default = Roles.APPLICANT,
        )

    def get_club_role(self):
        return self.Roles(self.club_role).name.title()

    def toggle_member(self):
        self.club_role = 'MEM'
        self.save()
        return
