from foodcartapp.models import GeoPositionAddress
from django.conf import settings
from geopy import distance
import requests


class CalculateDistanceError(TypeError):
    pass


def calculate_distances(order, available_restaurants_in_order, addresses_cache):
    address_cache = check_cache(order.address, addresses_cache)
    if not address_cache:
        delivery_coordinates = fetch_coordinates(
            settings.YANDEX_GEOCODER_TOKEN,
            order.address
            )
        if delivery_coordinates:
            lon, lat = delivery_coordinates
            GeoPositionAddress.objects.create(
                address=order.address,
                lon=lon,
                lat=lat
            )
        else:
            GeoPositionAddress.objects.create(
                address=order.address
            )
    else:
        delivery_coordinates = (address_cache.lon, address_cache.lat)

    available_restaurants = []
    for available_restaurant in available_restaurants_in_order:
        restaurans_coordinates = (
            available_restaurant.lon,
            available_restaurant.lat
            )
        if delivery_coordinates is None or None in delivery_coordinates:
            raise CalculateDistanceError('Не удалось расчитать расстояние')
        restaurant_distance = distance.distance(
            restaurans_coordinates,
            delivery_coordinates
            )
        available_restaurants.append(
            f"{available_restaurant}\n{restaurant_distance}"
            )
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
