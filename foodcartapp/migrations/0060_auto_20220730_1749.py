# Generated by Django 3.2 on 2022-07-30 14:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_auto_20220721_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geopositionaddress',
            name='lat',
            field=models.FloatField(blank=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='geopositionaddress',
            name='lon',
            field=models.FloatField(blank=True, verbose_name='долгота'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
