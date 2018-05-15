# Generated by Django 2.0.2 on 2018-04-22 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0002_auto_20171206_1447'),
        ('users', '0008_emailpixeluser_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailpixeluser',
            name='meeting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emailpixels', to='meetings.Meeting', verbose_name='Meeting'),
        ),
    ]