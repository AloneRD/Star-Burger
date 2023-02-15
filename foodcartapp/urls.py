from django.urls import path

from .views import (
    product_list_api,
    banners_list_api,
    get_orders_list,
    create_order, 
    update_order
    )


app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('orders/', get_orders_list, name='orders_list'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/update/<int:pk>/', update_order, name='update_order'),
]
