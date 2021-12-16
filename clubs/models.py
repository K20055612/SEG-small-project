from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import When
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from enum import Enum
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

"""Create a user model"""
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

    """Returns clubs that a user is in"""
    def get_user_clubs(self):
        return Club.objects.all().filter(
            club_members__username=self.username,role__club_role='MEM')|Club.objects.all().filter(
            club_members__username=self.username,role__club_role='OFF')|Club.objects.all().filter(
            club_members__username=self.username,role__club_role='OWN')

    """Returns clubs that a user has applied to"""
    def get_applied_clubs(self):
        return Club.objects.all().filter(club_members__username=self.username,role__club_role='APP')
        clubs = Club.objects.all()
        current_user = self
        user_applicant_clubs = Club.objects.all().filter(
            club_members__username = current_user.username,
            role__club_role='APP')
        user_clubs = Club.objects.all().filter(
            club_members__username = current_user.username).difference(user_applicant_clubs)
        return user_clubs


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

"""Create club model"""
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

    def get_club_role(self,user):
        return Role.objects.get(club = self, user = user).club_role

    """Changes user's role to member"""
    def toggle_member(self,user):
        role = Role.objects.get(club=self,user=user)
        role.club_role = 'MEM'
        role.save()

    """Changes user's role to officer"""
    def toggle_officer(self,user):
        role = Role.objects.get(club=self,user=user)
        if role.club_role == 'APP' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'OFF'
            role.save()
            return
    """Bans a user from club"""
    def ban_member(self,user):
        role = Role.objects.get(club=self,user=user)
        if role.club_role == 'MEM':
            role.club_role = 'BAN'
            role.save()
            return
        else:
            return
    """Unbans a banned user from club"""
    def unban_member(self,user):
        role = Role.objects.get(club=self,user=user)
        if role.club_role == 'BAN':
            """User must re-apply to re-join club"""
            role.delete()
            return
        else:
            return
    """Makes an officer the owner of the club"""
    def transfer_ownership(self,old_owner,new_owner):
        new_owner_role = Role.objects.get(club=self,user=new_owner)
        old_owner_role = Role.objects.get(club=self,user=old_owner)
        if new_owner_role.club_role == 'OFF':
            new_owner_role.club_role = 'OWN'
            new_owner_role.save()
            """Old owner becomes an officer at the club"""
            old_owner_role.club_role = 'OFF'
            old_owner_role.save()
            return
        else:
            return

    """Returns all user objects that are applicants of a club"""
    def get_applicants(self):
        return self.club_members.all().filter(
            club__club_name = self.club_name,
            role__club_role='APP')

    """Returns all user objects that are members of a club"""
    def get_members(self):
        return self.club_members.all().filter(
            club__club_name = self.club_name, role__club_role = 'MEM')

    """Returns all user objects that are in the club of a club"""
    def get_all_users_in_club(self):
        return self.club_members.all().filter(
            club__club_name = self.club_name, role__club_role = 'MEM')|self.club_members.all().filter(
                club__club_name = self.club_name, role__club_role = 'OFF')|self.club_members.all().filter(
                    club__club_name = self.club_name, role__club_role = 'OWN')

    """ Returns all banned users in the club"""
    def get_banned_members(self):
        return self.club_members.all().filter(
            club__club_name = self.club_name,
            role__club_role='BAN')

    """ Returns all officer users in the club"""
    def get_officers(self):
        return User.objects.all().filter(
            club__club_name = self.club_name,
            role__club_role='OFF')

    """Returns owner of club"""
    def get_owner(self):
        return User.objects.all().filter(
            club__club_name = self.club_name,
            role__club_role='OWN')

    """Checks if user is in club"""
    def is_user_in_club(self,user):
        try:
             role = self.get_club_role(user)
        except ObjectDoesNotExist:
            return False
        else:
            return True
    """Deletes user's role in the club"""
    def remove_user_from_club(self,user):
        role = Role.objects.get(club=self,user=user)
        role.delete()


"""Create role model"""
class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class RoleOptions(models.TextChoices):
        APPLICANT = 'APP', _('Applicant')
        MEMBER = 'MEM', _('Member')
        OFFICER = 'OFF', _('Officer')
        OWNER = 'OWN', _('Owner')
        BANNED = 'BAN',_('BannedMember')

    club_role = models.CharField(
        max_length = 3,
        choices = RoleOptions.choices,
        default = RoleOptions.APPLICANT,
        )

    def get_club_role(self):
        return self.RoleOptions(self.club_role).name.title()
