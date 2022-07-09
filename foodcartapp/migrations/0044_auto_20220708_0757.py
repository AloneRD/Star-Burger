# Generated by Django 3.2 on 2022-07-08 04:57

from django.db import migrations


def calculation_of_old_orders(apps, schema_editor):
    order_items = apps.get_model('foodcartapp', 'OrderItem')
    for order_item in order_items.objects.all():
        if order_item.cost == 0.00:
            cost = order_item.product.price * order_item.quantity
            order_item.cost = cost
            order_item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_orderitem_cost'),
    ]

    operations = [
        migrations.RunPython(calculation_of_old_orders)
    ]