from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
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
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
<<<<<<< HEAD
        chess_experience_level=self.faker.pyint(min_value=0,max_value=5)
=======
        chess_experience_level=self.faker.pyint(min_value=1,max_value=5)
        is_applicant=self.faker.boolean()
>>>>>>> applicant-list
        is_member=self.faker.boolean()
        is_officer=self.faker.boolean()
        is_owner=self.faker.boolean()

        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            bio=bio,
            chess_experience_level=chess_experience_level,
<<<<<<< HEAD
=======
            is_applicant=is_applicant,
>>>>>>> applicant-list
            is_member=is_member,
            is_officer=is_officer,
            is_owner=is_owner,

        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@fake.seed'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
