from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(),
    chess_experience_level = models.IntegerField(default=1)
