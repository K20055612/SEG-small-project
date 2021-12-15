from django.core.management.base import BaseCommand, CommandError
from clubs.models import User,Club,Role

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(username__contains='@fake.seed').delete()
        Club.objects.filter(location__contains='Test').delete()
