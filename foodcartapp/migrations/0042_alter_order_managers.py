# Generated by Django 3.2 on 2022-07-06 20:21

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20220704_2326'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
                ('custom_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
