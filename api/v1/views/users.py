#!/usr/bin/python3
"""View to handle API actions related to User objects
"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.user import User

@app_views.route('/users', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/users/<user_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def users_method(user_id=None):
    """Manipulate User object by user_id, or all objects if user_id is None"""
    if request.method == 'GET':
        return get_request(User, user_id)
    elif request.method == 'DELETE':
        return delete_request(User, user_id)
    elif request.method == 'POST':
        return post_request(User)
    elif request.method == 'PUT':
        return put_request(User, user_id)
    else:
        abort(501)


def get_request(model, obj_id=None):
    """Handles GET requests for the specified model"""
    objects = storage.all(model)
    if obj_id is None:
        return jsonify([obj.to_dict() for obj in objects.values()])

    key = f'{model.__name__}.{obj_id}'
    obj = objects.get(key)
    if obj:
        return jsonify(obj.to_dict())
    else:
        abort(404)


def delete_request(model, obj_id):
    """Handles DELETE requests for the specified model"""
    key = f'{model.__name__}.{obj_id}'
    objects = storage.all(model)
    obj = objects.get(key)
    if obj:
        storage.delete(obj)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


def post_request(model):
    """Handles POST requests for the specified model"""
    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()

    if model == User:
        if 'email' not in body_request:
            abort(400, 'Missing email')
        elif 'password' not in body_request:
            abort(400, 'Missing password')

    new_obj = model(**body_request)
    storage.new(new_obj)
    storage.save()
    return jsonify(new_obj.to_dict()), 201


def put_request(model, obj_id):
    """Handles PUT requests for the specified model"""
    key = f'{model.__name__}.{obj_id}'
    objects = storage.all(model)
    obj = objects.get(key)
    if obj is None:
        abort(404)

    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()
    for key, value in body_request.items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(obj, key, value)

    storage.save()
    return jsonify(obj.to_dict()), 200
