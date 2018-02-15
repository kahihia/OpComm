# Generated by Django 2.0 on 2018-02-15 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_ocuser_uid'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnsubscribeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unsubscribes', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]