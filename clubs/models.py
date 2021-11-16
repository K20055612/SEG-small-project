from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

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
