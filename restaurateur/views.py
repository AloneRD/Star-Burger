from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, OrderItem
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem

from restaurateur.geo_distance import calculate_restoraunts_distances


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = OrderItem.objects.select_related("product")
    pending_orders = Order.custom_manager\
        .prefetch_related(Prefetch('items', queryset=order_items))\
        .prefetch_related('order_fulfilling_restaurant')\
        .calculate_total_cost_of_order_items()\
        .order_by('id')\
        .filter(status="Необработанный")
    restaurants_menu = RestaurantMenuItem.objects.select_related('product').select_related('restaurant')
    for pending_order in pending_orders:
        available_restaurants_in_order = []
        pending_order_items = pending_order.items.all()
        pending_order_producs = [pending_order_item.product for pending_order_item in pending_order_items]
        for product in pending_order_producs:
            available_restaurants_for_product = [menu_item.restaurant for menu_item in restaurants_menu if menu_item.product==product]
            available_restaurants_in_order.append(available_restaurants_for_product)
        if len(available_restaurants_in_order) > 1:
            for restaurant_number, restaurant in enumerate(available_restaurants_in_order):
                try:
                    available_restaurants_in_order[restaurant_number] = list(set(available_restaurants_in_order[restaurant_number]) & set(available_restaurants_in_order[restaurant_number+1]))
                except IndexError:
                    pass
        pending_order = calculate_restoraunts_distances(pending_order, available_restaurants_in_order[0])
    return render(request, template_name='order_items.html', context={
        'orders': pending_orders,
    })
