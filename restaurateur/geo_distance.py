from foodcartapp.models import Order, OrderItem, GeoPositionAddress
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from geopy import distance
import requests


def calculate_distances_restaurants(order, available_restaurants_in_order):
    try:
        address_cache = GeoPositionAddress.objects.get(address=order.address)
        lon, lat = (address_cache.lon, address_cache.lat)
        delivery_coordinates = (lon, lat)
    except ObjectDoesNotExist:
        delivery_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, order.address)
        lon, lat = delivery_coordinates
        GeoPositionAddress.objects.create(
            address=order.address,
            lon=lon,
            lat=lat
        )
    available_restaurants = []
    if available_restaurants_in_order:
        for available_restaurant in available_restaurants_in_order:
            restaurans_coordinates = (available_restaurant.lon, available_restaurant.lat)
            restaurant_distance = distance.distance(restaurans_coordinates, delivery_coordinates)
            restaurant = f"{available_restaurant} {restaurant_distance}"
            available_restaurants.append(restaurant)
    order.available_restaurants = available_restaurants
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