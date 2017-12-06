# Generated by Django 2.0 on 2017-12-06 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address')),
                ('display_name', models.CharField(max_length=200, verbose_name='Your name')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('message', models.TextField(blank=True, null=True, verbose_name='Message')),
                ('code', models.CharField(default=users.models.create_code, max_length=48)),
                ('default_group_name', models.CharField(choices=[('member', 'member'), ('board', 'board'), ('secretary', 'secretary'), ('chairman', 'chairman')], max_length=50, verbose_name='Group')),
                ('status', models.PositiveIntegerField(choices=[(0, 'Pending'), (1, 'Sent'), (2, 'Failed')], default=0, verbose_name='Status')),
                ('times_sent', models.PositiveIntegerField(default=0, verbose_name='Times Sent')),
                ('error_count', models.PositiveIntegerField(default=0, verbose_name='Error count')),
                ('last_sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Sent at')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invitations', to='communities.Community', verbose_name='Community')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invitations_created', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invitations', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Invitation',
                'verbose_name_plural': 'Invitations',
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_group_name', models.CharField(choices=[('member', 'member'), ('board', 'board'), ('secretary', 'secretary'), ('chairman', 'chairman')], max_length=50, verbose_name='Group')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('in_position_since', models.DateField(default=django.utils.timezone.now, verbose_name='In position since')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='memberships', to='communities.Community', verbose_name='Community')),
                ('invited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='members_invited', to=settings.AUTH_USER_MODEL, verbose_name='Invited by')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='memberships', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Community Member',
                'verbose_name_plural': 'Community Members',
            },
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together={('community', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together={('community', 'email')},
        ),
    ]
