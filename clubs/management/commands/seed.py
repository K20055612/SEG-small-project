from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User,Club,Role

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 30
    CLUB_COUNT = 4

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        club_count = 0
        self._create_test_data()
        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}',  end='\r')
            try:
                self._create_club()
            except (django.db.utils.IntegrityError):
                continue
            club_count += 1

        print('Club seeding complete')

        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def _create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        username = self._email(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        chess_experience_level=self.faker.pyint(min_value=1,max_value=5)

        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            password=Command.PASSWORD,
            bio=bio,
            chess_experience_level=chess_experience_level,
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@fake.seed'
        return email

    def _create_club(self):
        club_name = self.faker.first_name()
        location = 'Test'
        description = self.faker.text(max_nb_chars=520)

        Club.objects.create(
                club_name=club_name,
                location=location,
                description=description,
            )

    def _create_test_data(self):

        jebediah = User.objects.create(username="jeb@example.org",first_name="Jebebiah",last_name="Kerman",
        password='pbkdf2_sha256$260000$LnafUF8ekxltY63RK2jDbQ$v/g4SLvK1DV/sMFd0u4e38pWzVHWNrBXLdXsjPE4d9E=',bio="Hi guys",chess_experience_level=4)


        valentina = User.objects.create(username="val@example.org",first_name="Valentina",last_name="Kerman",
        bio="Hi guys",chess_experience_level=2,password='pbkdf2_sha256$260000$LnafUF8ekxltY63RK2jDbQ$v/g4SLvK1DV/sMFd0u4e38pWzVHWNrBXLdXsjPE4d9E=')

        billie = User.objects.create(username="billie@example.org",first_name="Billie",last_name="Kerman",
        password='pbkdf2_sha256$260000$LnafUF8ekxltY63RK2jDbQ$v/g4SLvK1DV/sMFd0u4e38pWzVHWNrBXLdXsjPE4d9E=',bio="Hi guys",chess_experience_level=4)

        kerbal_club = Club.objects.create(club_name="Kerbal Chess Club",location="Test",description="Welcome to the Kerbals!")
        atlantis_club = Club.objects.create(club_name="Atlantis",location="Test",description="Welcome to the Atlantis!")

        atlantis_club.club_members.add(billie,through_defaults={'club_role':'APP'})
        atlantis_club.club_members.add(valentina,through_defaults={'club_role':'OFF'})

        kerbal_club.club_members.add(jebediah,through_defaults={'club_role':'APP'})
        kerbal_club.club_members.add(valentina,through_defaults={'club_role':'APP'})
        kerbal_club.club_members.add(billie,through_defaults={'club_role':'OFF'})
