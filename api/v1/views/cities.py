#!/usr/bin/python3
"""New view for City objects that handles all default RestFul API actions
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.state import State
from models.city import City


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'],
                 strict_slashes=False)
def city_methods(state_id):
    """Calls method for City object with state_id"""
    if request.method == "GET":
        return get_request(City, relationship=State, parent_id=state_id)
    elif request.method == "POST":
        return post_request(City, State, state_id)

@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def cities_id_methods(city_id):
    """Handles HTTP methods for City objects based on city_id."""
    if request.method == "GET":
        return get_request(City, city_id)
    elif request.method == "DELETE":
        return delete_request(City, city_id)
    elif request.method == "PUT":
        return put_request(City, city_id)


def get_request(model, obj_id=None, relationship=None, parent_id=None):
    """Handles GET requests for any model object."""
    objects = storage.all(model)
    if obj_id is None:
        return jsonify([obj.to_dict() for obj in objects.values()])

    key = f'{model.__name__}.{obj_id}'
    obj = objects.get(key)
    if obj:
        if relationship and parent_id:
            parent_key = f'{relationship.__name__}.{parent_id}'
            parent = storage.all(relationship).get(parent_key)
            if parent:
                related_objs = [related_obj.to_dict() for related_obj in getattr(parent, relationship.__name__.lower() + 's')]
                return jsonify(related_objs)
            else:
                abort(404)
        return jsonify(obj.to_dict())
    else:
        abort(404)


def delete_request(model, obj_id):
    """Handles DELETE requests for any model object."""
    key = f'{model.__name__}.{obj_id}'
    objects = storage.all(model)
    obj = objects.get(key)
    if obj:
        storage.delete(obj)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


def put_request(model, obj_id):
    """Handles PUT requests for any model object."""
    key = f'{model.__name__}.{obj_id}'
    objects = storage.all(model)
    obj = objects.get(key)
    if obj is None:
        abort(404)

    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()
    for key, value in body_request.items():
        if key not in ['id', 'state_id', 'created_at', 'updated_at']:
            setattr(obj, key, value)

    storage.save()
    return jsonify(obj.to_dict()), 200


def post_request(model, relationship, parent_id):
    """Handles POST requests to create a new object."""
    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()
    if 'name' not in body_request:
        abort(400, 'Missing name')

    parent_key = f'{relationship.__name__}.{parent_id}'
    parent = storage.all(relationship).get(parent_key)
    if parent is None:
        abort(404)

    body_request.update({relationship.__name__.lower() + '_id': parent_id})
    new_obj = model(**body_request)
    storage.new(new_obj)
    storage.save()
    return jsonify(new_obj.to_dict()), 201

