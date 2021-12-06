# Generated by Django 3.2.5 on 2021-12-06 17:29

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('bio', models.CharField(blank=True, max_length=520)),
                ('chess_experience_level', models.IntegerField(choices=[(1, 'Beginner'), (2, 'Experienced'), (3, 'Intermediate'), (4, 'Advanced'), (5, 'Expert')], default=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Club name must consist of at least four alphanumericals in first word', regex='^\\w{4,}.*$')])),
                ('location', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=520)),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enter_by_deadline', models.DateTimeField()),
                ('tournament_name', models.CharField(max_length=20, unique=True)),
                ('tournament_capacity', models.IntegerField(validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(96)])),
                ('tournament_description', models.CharField(max_length=520)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tournament_role', models.CharField(choices=[('ORG', 'Organiser'), ('PLA', 'Player')], default='PLA', max_length=3)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='tournament',
            name='tournament_participants',
            field=models.ManyToManyField(through='clubs.TournamentRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_role', models.CharField(choices=[('APP', 'Applicant'), ('MEM', 'Member'), ('OFF', 'Officer'), ('OWN', 'Owner')], default='APP', max_length=3)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_points', models.IntegerField()),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Opponent1', to='clubs.player')),
                ('player2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Opponent2', to='clubs.player')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_winner', to='clubs.player')),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='club_members',
            field=models.ManyToManyField(through='clubs.Role', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='club',
            name='club_tournaments',
            field=models.ManyToManyField(related_name='tournament_at_club', to='clubs.Tournament'),
        ),
    ]
