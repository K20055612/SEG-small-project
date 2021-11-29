from django.contrib.auth import authenticate
from .models import User

class CustomBackend(object):
    #check if email and password are correct
    def authenticate(self,request,username=None,password=None,**kwargs):
        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user

    def get_user(self, id=None):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
