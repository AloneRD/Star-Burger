from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.db import transaction
from django.db.models import Prefetch

from .models import Order
from .models import OrderItem
from .models import Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'items']

    def create(self, validated_data):
        items = validated_data.pop('items')
        order = Order.custom_manager.create(**validated_data)
        for item in items:
            item['order_position_total_cost'] = item['product'].price * item['quantity']
            OrderItem.objects.create(order=order, **item)
        return order
    
    def update(self, instance, validated_data):
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.phonenumber = validated_data.get('phonenumber', instance.phonenumber)
        instance.address = validated_data.get('address', instance.address)
        for item in validated_data.get('items', instance.items.all()):
            item['order_position_total_cost'] = item['product'].price * item['quantity']
            OrderItem.objects.filter(order=instance).update(**item)
        instance.save()
        return instance

@api_view(['GET'])
def get_orders_list(request):
    order_items = OrderItem.objects.select_related("product")
    queryset = Order.custom_manager\
        .prefetch_related(Prefetch('items', queryset=order_items))
    serializer = OrderSerializer(instance=queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@transaction.atomic
def create_order(request):
    received_order = request.data
    serializer = OrderSerializer(data=received_order)
    serializer.is_valid()
    serializer.save()
    return Response(serializer.data)

@api_view(['POST', 'GET'])
@transaction.atomic
def update_order(request, pk):
    order_items = OrderItem.objects.select_related("product")
    order = Order.custom_manager\
        .prefetch_related(Prefetch('items', queryset=order_items)).get(id=pk)
    if request.method == "GET":
        serializer = OrderSerializer(instance=order)
    elif request.method == "POST":
        serializer = OrderSerializer(order, data=request.data)
        serializer.is_valid()
        serializer.save()
    return Response(serializer.data)
