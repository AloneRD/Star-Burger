import requests
from geopy import distance
from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, OrderItem
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem


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
    pending_orders = Order.custom_manager.prefetch_related(Prefetch('items', queryset=order_items)).prefetch_related('restaurant').summa().order_by('id').filter(status="Необработанный")
    restaurants_menu = RestaurantMenuItem.objects.select_related('product').select_related('restaurant')
    for pending_order in pending_orders:
        available_restaurants_in_order = []
        pending_order_items = pending_order.items.all()
        pending_order_producs = [pending_order_item.product for pending_order_item in pending_order_items]
        for product in pending_order_producs:
            available_restaurants_for_product = [menu_item.restaurant.name for menu_item in restaurants_menu if menu_item.product==product]
            available_restaurants_in_order.append(available_restaurants_for_product)
        if len(available_restaurants_in_order)>1:
            for restaurants in range(len(available_restaurants_in_order)-1):
                available_restaurants_in_order[restaurants] = list(set(available_restaurants_in_order[restaurants]) & set(available_restaurants_in_order[restaurants+1]))
        pending_order = calculation_of_distance_restaurants(pending_order, available_restaurants_in_order[0])
        print(pending_order.available_restaurants)
    return render(request, template_name='order_items.html', context={
        'orders': pending_orders,
    })


def calculation_of_distance_restaurants(order, available_restaurants_in_order):
    deleverey_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, order.address)
    available_restaurants = []
    if len(available_restaurants_in_order) > 0:
        for restaurant in available_restaurants_in_order:
            restaurans_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, restaurant)
            distance_restaurants = distance.distance(restaurans_coordinates, deleverey_coordinates)
            restaurant = f"{restaurant} {distance_restaurants}"
            available_restaurants.append(restaurant)
    order.available_restaurants = ' '.join(available_restaurants)
    return order


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
