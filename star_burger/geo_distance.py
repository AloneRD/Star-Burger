from foodcartapp.models import Order, OrderItem, GeoPositionAddress
from django.conf import settings
from geopy import distance
import requests


def calculation_of_distance_restaurants(order, available_restaurants_in_order):
    try:
        cache_address = GeoPositionAddress.objects.get(address=str(order.address))
        deleverey_coordinates = (cache_address.lon, cache_address.lat)
    except:
        deleverey_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_TOKEN, order.address)
        GeoPositionAddress.objects.create(
            address=order.address,
            lon=deleverey_coordinates[0],
            lat=deleverey_coordinates[1]
        )
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