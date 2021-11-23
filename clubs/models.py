from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import When
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar



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
    chess_experience_level = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=5)
            ]
    )

    is_member = models.BooleanField(default = False)

    def toggle_member(user):
        if user.is_member == True:
            return
        elif user.is_member == False:
            user.is_member == True

    is_officer = models.BooleanField(default = False)

    is_owner = models.BooleanField(default = False)

    def toggle_officer(user):
        if user.is_owner == True:
            return
        elif user.is_officer == False:
            user.is_officer == True


    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url
