from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import When
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from enum import Enum
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.EmailField(
        unique=True,
        blank=False
        )

    first_name = models.CharField(
        max_length=50,
        blank=False
    )
    last_name = models.CharField(
        max_length=50,
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

    def get_chess_experience(self):
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
    unique=True,
    max_length=50,
    blank=False,
    validators=[
        RegexValidator(
            regex=r'^\w{5,}$',
            message='Club name must consist of at least five alphanumericals'
            )
        ]
    )
    location = models.CharField(
        max_length=100,
        blank=False
        )

    description = models.CharField(
        max_length=520,
        blank=False
        )

    club_members = models.ManyToManyField(User,through='Role')

class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class RoleOptions(models.TextChoices):
        APPLICANT = 'APP', _('Applicant')
        MEMBER = 'MEM', _('Member')
        OFFICER = 'OFF', _('Officer')
        OWNER = 'OWN', _('Owner')

    club_role = models.CharField(
        max_length = 3,
        choices = RoleOptions.choices,
        default = RoleOptions.APPLICANT,
        )

    def get_club_role(self):
        return self.RoleOptions(self.club_role).name.title()

    def toggle_member(self):
        self.club_role = 'MEM'
        self.save()
        return

    def toggle_officer(self):
        if self.club_role == 'APP':
            return
        else:
            self.club_role = 'OFF'
            self.save()
            return

    def transfer_ownership(self,new_owner):
        if new_owner.club_role == 'OFF':
            new_owner.club_role = 'OWN'
            new_owner.save()
            self.club_role = 'OFF'
            self.save()
            return
        else:
            return
