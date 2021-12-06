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
        blank=False,
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
    max_length=20,
    blank=False,
    validators=[
        RegexValidator(
            regex=r'^\w{4,}.*$',
            message='Club name must consist of at least four alphanumericals in first word'
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

    club_tournaments = models.ManyToManyField('Tournament',related_name='tournament_at_club')


    def get_club_role(self,user):
        return Role.objects.get(club = self, user = user).club_role

    def get_tournaments(self):
        return self.club_tournaments.all()

    def toggle_member(self,user):
        role = Role.objects.get(club=self,user=user)
        role.club_role = 'MEM'
        role.save()

    def toggle_officer(self,user):
        role = Role.objects.get(club=self,user=user)
        if role.club_role == 'APP':
            return
        else:
            role.club_role = 'OFF'
            role.save()
            return

    def transfer_ownership(self,old_owner,new_owner):
        new_owner_role = Role.objects.get(club=self,user=new_owner)
        old_owner_role = Role.objects.get(club=self,user=old_owner)
        if new_owner_role.club_role == 'OFF':
            new_owner_role.club_role = 'OWN'
            new_owner_role.save()
            old_owner_role.club_role = 'OFF'
            old_owner_role.save()
            return
        else:
            return

    def get_applicants(self):
        return User.objects.all().filter(
            club__club_name = self.club_name,
            role__club_role='APP')

    def get_members(self):
        return User.objects.all().filter(
            club__club_name = self.club_name, role__club_role = 'MEM') | User.objects.all().filter(
                club__club_name = self.club_name, role__club_role = 'OFF') | User.objects.all().filter(
                    club__club_name = self.club_name, role__club_role = 'OWN')


    def get_officers(self):
        return User.objects.all().filter(
            club__club_name = self.club_name,
            role__club_role='OFF')

    def remove_user_from_club(self,user):
        role = Role.objects.get(club=self,user=user)
        role.delete()

class Tournament(models.Model):
    club = models.ForeignKey(Club,on_delete=models.CASCADE)
    organiser = models.ManyToManyField(User,related_name='organising_officers')
    enter_by_deadline = models.DateTimeField(auto_now=False)
    tournament_name = models.CharField(
    unique=True,
    max_length=20,
    blank=False,)
    tournament_capacity = models.IntegerField(
    validators=[MinValueValidator(2),MaxValueValidator(96)]
    )
    tournament_description = models.CharField(
        max_length=520,
        blank=False
        )

    tournament_participants = models.ManyToManyField(User, through='Player')

    def get_deadline(self):
        return datetime.now() > self.enter_by_deadline

    def get_organisers(self):
        return self.organiser.all()

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player_points = models.IntegerField()

class Match(models.Model):
    player1 = models.ForeignKey(Player,related_name = 'Opponent1',on_delete=models.CASCADE)

    player2 = models.ForeignKey(Player, related_name = 'Opponent2',on_delete=models.CASCADE)

    winner = models.ForeignKey(Player, related_name='match_winner',on_delete=models.CASCADE)

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
