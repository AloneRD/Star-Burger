# Generated by Django 3.2 on 2022-07-20 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_rename_geopositionrestaurant_geopositionaddress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geopositionaddress',
            name='address',
            field=models.CharField(db_index=True, max_length=500, unique=True, verbose_name='адрес доставки'),
        ),
    ]
