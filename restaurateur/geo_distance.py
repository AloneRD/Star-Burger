from foodcartapp.models import GeoPositionAddress
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from geopy import distance
import requests


def calculate_distances(order, available_restaurants_in_order, addresses_cache):
    address_cache = check_cache(order.address, addresses_cache)
    if not address_cache:
        delivery_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, order.address)
        if delivery_coordinates:
            lon, lat = delivery_coordinates
            GeoPositionAddress.objects.create(
                address=order.address,
                lon=lon,
                lat=lat
            )
    else:
        lon, lat = (address_cache.lon, address_cache.lat)
        delivery_coordinates = (lon, lat)

    available_restaurants = []
    for available_restaurant in available_restaurants_in_order:
        if not available_restaurant:
            continue
        restaurans_coordinates = (available_restaurant.lon, available_restaurant.lat)
        restaurant_distance = distance.distance(restaurans_coordinates, delivery_coordinates)
        restaurant = f"{available_restaurant} {restaurant_distance}"
        available_restaurants.append(restaurant)
    order.available_restaurants = available_restaurants
    return order


def check_cache(order_address, addresses_cache):
    for address_cache in addresses_cache:
        if address_cache.address == order_address:
            return address_cache
    return False


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
