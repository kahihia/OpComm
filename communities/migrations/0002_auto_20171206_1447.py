# Generated by Django 2.0 on 2017-12-06 12:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='upcoming_meeting_participants',
            field=models.ManyToManyField(blank=True, related_name='_community_upcoming_meeting_participants_+', to=settings.AUTH_USER_MODEL, verbose_name='Participants in upcoming meeting'),
        ),
        migrations.AlterUniqueTogether(
            name='communityconfidentialreason',
            unique_together={('community', 'title')},
        ),
    ]
