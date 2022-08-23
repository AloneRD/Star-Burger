# Generated by Django 3.2 on 2022-08-23 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0062_auto_20220730_1809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='cost',
            new_name='order_total_cost',
        ),
        migrations.AlterField(
            model_name='geopositionaddress',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='geopositionaddress',
            name='lon',
            field=models.FloatField(blank=True, null=True, verbose_name='долгота'),
        ),
    ]