from django.core.management.base import BaseCommand, CommandError
from faker import Faker
import random
from clubs.models import User,Club,Role
from django.core import management
from django.db.utils import IntegrityError

class Command(BaseCommand):

    PASSWORD = "Password123"
    USER_COUNT = 30
    CLUB_COUNT = 4

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        management.call_command('loaddata', 'clubs/management/commands/fixtures/required_clubs.json')
        management.call_command('loaddata', 'clubs/management/commands/fixtures/required_users.json')
        self._create_required_roles()

        user_count = 0
        club_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except IntegrityError as e:
                continue
            user_count += 1
        print('User seeding complete')

        while club_count < Command.CLUB_COUNT:
            try:
                self._create_club()
            except IntegrityError as e:
                continue
            club_count += 1

        print('Club seeding complete')

    def _create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        username = self._email(first_name, last_name)
        bio = "Hi, my name is " + first_name + " " + last_name
        chess_experience_level=self.faker.pyint(min_value=1,max_value=5)

        User.objects.create_user(
            username = username,
            first_name=first_name,
            last_name=last_name,
            password=Command.PASSWORD,
            bio=bio,
            chess_experience_level=chess_experience_level,
        )


    def _email(self, first_name, last_name):
        email = f'{first_name.lower()}.{last_name.lower()}@example.org'
        return email

    def _create_club(self):
        club_name = self.faker.word().capitalize() + " Chess Club"
        location = 'London'
        description = "At " + club_name + " our aim is make you the best chess player you can be."

        new_club = Club.objects.create(
                club_name=club_name,
                location=location,
                description=description,
            )

        self._create_club_roles(new_club)

    def _create_club_roles(self,club):
        club_owner=random.choice(User.objects.all())
        club.club_members.add(club_owner,through_defaults={'club_role':'OWN'})

        club_roles = ['APP','MEM','OFF','BAN']
        for user_number in range(1, int(self.USER_COUNT/3)):
            current_user = random.choice(User.objects.all().difference(club.get_all_users_in_club()))
            club.club_members.add(current_user,through_defaults={'club_role':random.choice(club_roles)})

    def _create_required_roles(self):

        jebediah = User.objects.get(username='jeb@example.org')
        valentina = User.objects.get(username='val@example.org')
        billie = User.objects.get(username='billie@example.org')

        kerbal_club = Club.objects.get(club_name='Kerbal Chess Club')
        london_chess_club = Club.objects.get(club_name='London Chess Club')
        elite_chess_club = Club.objects.get(club_name='Elite Chess Club')
        house_of_dukes = Club.objects.get(club_name='House of Dukes')

        kerbal_club.club_members.add(jebediah,through_defaults={'club_role':'MEM'})
        kerbal_club.club_members.add(valentina,through_defaults={'club_role':'OFF'})
        kerbal_club.club_members.add(billie,through_defaults={'club_role':'OWN'})

        london_chess_club.club_members.add(jebediah,through_defaults={'club_role':'OFF'})
        london_chess_club.club_members.add(billie,through_defaults={'club_role':'OWN'})

        elite_chess_club.club_members.add(valentina,through_defaults={'club_role':'OWN'})

        house_of_dukes.club_members.add(billie,through_defaults={'club_role':'MEM'})
        house_of_dukes.club_members.add(jebediah,through_defaults={'club_role':'OWN'})
