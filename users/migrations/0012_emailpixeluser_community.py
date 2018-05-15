# Generated by Django 2.0.2 on 2018-04-29 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0004_meetingattachment'),
        ('users', '0011_auto_20180429_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailpixeluser',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emailpixels', to='communities.Community', verbose_name='Community'),
        ),
    ]
