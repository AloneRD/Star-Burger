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
    def to_representation(self, obj):
        new_obj = {'product': obj.product.name, 'quantity':obj.quantity}
        return new_obj
        
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'items']


@api_view(['POST', 'GET'])
@transaction.atomic
def order_api(request):
    if request.method == 'GET':
        order_items = OrderItem.objects.select_related("product")
        queryset = Order.custom_manager\
            .prefetch_related(Prefetch('items', queryset=order_items))
        serializer = OrderSerializer(instance=queryset, many=True)
    elif request.method == 'POST':
        received_order = request.data
        serializer = OrderSerializer(data=received_order)
        serializer.is_valid(raise_exception=True)
        new_order = Order.custom_manager.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address']
        )
        order_items = [OrderItem(order=new_order, **fields) for fields in serializer.validated_data['products']]
        for order_item in order_items:
            order_item.cost = order_item.quantity * order_item.product.price
        OrderItem.objects.bulk_create(order_items)

    return Response(serializer.data)
