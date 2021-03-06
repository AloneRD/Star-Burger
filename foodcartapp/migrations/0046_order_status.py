# Generated by Django 3.2 on 2022-07-09 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_alter_orderitem_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('RAW', 'Необработан'), ('ASSEMBLY', 'Сборка'), ('DELIVER', 'Доставка'), ('COMPLETED', 'Завершен')], db_index=True, default='RAW', max_length=50, verbose_name='статус'),
        ),
    ]
