#!/usr/bin/python3
"""Places view API request handlers
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.amenity import Amenity


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Search for places according to parameters in body request."""
    if request.is_json:
        body = request.get_json()
    else:
        abort(400, 'Not a JSON')

    return search_places(body)


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'], strict_slashes=False)
def places_by_city_requests(city_id):
    """Perform API requests of places by city."""
    if request.method == 'GET':
        return get_places_by_city(city_id)
    elif request.method == 'POST':
        return create_place(city_id)
    else:
        abort(501)


@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def place_methods(place_id=None):
    """Perform API requests on place objects."""
    if request.method == 'GET':
        return get_place_by_id(place_id)
    elif request.method == 'DELETE':
        return delete_place_by_id(place_id)
    elif request.method == 'PUT':
        return update_place_by_id(place_id)
    else:
        abort(501)


# Helper functions for request handling
def get_place_by_id(place_id):
    """Retrieve a specific Place object by ID."""
    places = storage.all(Place)
    try:
        key = 'Place.' + place_id
        return jsonify(places[key].to_dict())
    except KeyError:
        abort(404)


def delete_place_by_id(place_id):
    """Delete a specific Place object by ID."""
    places = storage.all(Place)
    try:
        key = 'Place.' + place_id
        storage.delete(places[key])
        storage.save()
        return jsonify({}), 200
    except KeyError:
        abort(404)


def update_place_by_id(place_id):
    """Update a specific Place object by ID."""
    places = storage.all(Place)
    key = 'Place.' + place_id
    try:
        place = places[key]
        if request.is_json:
            body_request = request.get_json()
        else:
            abort(400, 'Not a JSON')

        ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
        for key, val in body_request.items():
            if key not in ignore:
                setattr(place, key, val)

        storage.save()
        return jsonify(place.to_dict()), 200
    except KeyError:
        abort(404)


def search_places(body):
    """Search for places based on provided criteria."""
    place_list = []

    # Search by states
    if 'states' in body:
        for state_id in body['states']:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    for place in city.places:
                        place_list.append(place)

    # Search by cities
    if 'cities' in body:
        for city_id in body['cities']:
            city = storage.get(City, city_id)
            if city:
                for place in city.places:
                    place_list.append(place)

    # Filter by amenities
    if 'amenities' in body and body['amenities']:
        if not place_list:
            place_list = [place for place in storage.all(Place).values()]
        del_list = []
        for place in place_list:
            for amenity_id in body['amenities']:
                amenity = storage.get(Amenity, amenity_id)
                if amenity not in place.amenities:
                    del_list.append(place)
                    break
        for place in del_list:
            place_list.remove(place)

    if not place_list:
        place_list = [place for place in storage.all(Place).values()]

    place_list = [place.to_dict() for place in place_list]
    for place in place_list:
        place.pop('amenities', None)

    return jsonify(place_list)


def create_place(city_id):
    """Create a new Place object within a specific City."""
    cities = storage.all(City)

    if ('City.' + city_id) not in cities:
        abort(404)

    if request.is_json:
        body_request = request.get_json()
    else:
        abort(400, 'Not a JSON')

    if 'name' not in body_request:
        abort(400, 'Missing name')
    if 'user_id' not in body_request:
        abort(400, 'Missing user_id')

    users = storage.all(User)
    if ('User.' + body_request['user_id']) not in users:
        abort(404)

    body_request.update({'city_id': city_id})
    new_place = Place(**body_request)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201

