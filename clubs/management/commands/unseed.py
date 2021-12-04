from django.core.management.base import BaseCommand, CommandError
from clubs.models import User,Club,Role

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(username__contains='@fake.seed').delete()
        User.objects.filter(username__contains='@example.org').delete()
        Club.objects.filter(location__contains='Test').delete()
        Role.objects.filter(club_role__contains='APP').delete()
        Role.objects.filter(club_role__contains='OFF').delete()
        Role.objects.filter(club_role__contains='MEM').delete()
        Role.objects.filter(club_role__contains='OWN').delete()
