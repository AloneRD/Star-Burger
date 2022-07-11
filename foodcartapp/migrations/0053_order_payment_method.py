# Generated by Django 3.2 on 2022-07-11 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_alter_orderitem_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Электронно', 'Электронно'), ('Наличностью', 'Наличностью')], db_index=True, default='Наличностью', max_length=500, verbose_name='способ оплаты'),
        ),
    ]
