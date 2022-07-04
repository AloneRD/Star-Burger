from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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

@api_view(['POST'])
def register_order(request):
    received_order = request.data
    try:
        order_items, firstname, last_name, phone, delivery_address = received_order.values()
    except:
        content = {"error": "required fields are not filled"}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not firstname and not last_name and not phone and not delivery_address:
        content = {"error": "firstname, lastname, phonenumber, address: can not be empty"}
    elif not isinstance(firstname, str):
        content = {"error": "firstname: Not a valid string"}
    elif not firstname:
        content = {"error": "firstname: can not be empty"}
    elif not isinstance(order_items, list):
        content = {"error": "products: Expected a list with values, but got 'str'"}
    elif not order_items or len(order_items) == 0:
        content = {"error": "products can not be empty"}
    elif not phone:
        content = {"error": "phone: can not be empty"}
    elif phone.count('0') > 9:
        content = {"error": "phonenumber: Invalid phone number entered"}
    if 'content' in locals():
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    new_order = Order.objects.create(
        first_name=firstname,
        last_name=last_name,
        phone=phone,
        delivery_address=delivery_address
    )
    for order_item in order_items:
        product_id, quantity = order_item.values()
        try:
            product = Product.objects.get(id=product_id)
        except:
            content = {"error": "products: Invalid primary key 'product_id'"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        OrderItem.objects.create(
            order=new_order,
            product=product,
            quantity=quantity
        )
    return Response({})
