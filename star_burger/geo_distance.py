from foodcartapp.models import Order, OrderItem, GeoPositionAddress
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from geopy import distance
import requests


def calculate_distances_restaurants(order, available_restaurants_in_order):
    try:
        adress_cache = GeoPositionAddress.objects.get(address=order.address)
        lon, lat = (adress_cache.lon, adress_cache.lat)
        deleverey_coordinates = (lon, lat)
    except ObjectDoesNotExist:
        deleverey_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, order.address)
        GeoPositionAddress.objects.create(
            address=order.address,
            lon=lon,
            lat=lat
        )
    available_restaurants = []
    if len(available_restaurants_in_order) > 0:
        for restaurant in available_restaurants_in_order:
            restaurans_coordinates = (restaurant.lon, restaurant.lat)
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