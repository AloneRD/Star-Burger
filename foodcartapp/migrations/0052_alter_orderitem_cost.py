# Generated by Django 3.2 on 2022-07-11 04:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_auto_20220711_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость'),
        ),
    ]
