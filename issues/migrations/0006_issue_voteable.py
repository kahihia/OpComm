# Generated by Django 2.0 on 2017-12-19 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0005_auto_20171214_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='voteable',
            field=models.BooleanField(default=False, verbose_name='Open for voting'),
        ),
    ]