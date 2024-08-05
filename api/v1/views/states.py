#!/usr/bin/python3
"""
Flask route that returns a JSON status response for State objects
"""
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET', 'POST'], strict_slashes=False)
@app_views.route('/states/<state_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def states_route(state_id=None):
    """
    Delegates requests to appropriate function based on HTTP method.
    """
    if request.method == 'GET':
        return get_request(state_id)
    elif request.method == 'DELETE':
        return delete_request(state_id)
    elif request.method == 'POST':
        return post_request()
    elif request.method == 'PUT':
        return put_request(state_id)
    else:
        abort(501)


def get_request(state_id=None):
    """Handles GET requests for State objects."""
    states = storage.all(State)
    if state_id is None:
        return jsonify([obj.to_dict() for obj in states.values()])

    key = f'State.{state_id}'
    state = states.get(key)
    if state:
        return jsonify(state.to_dict())
    else:
        abort(404)


def delete_request(state_id):
    """Handles DELETE requests for State objects."""
    key = f'State.{state_id}'
    states = storage.all(State)
    state = states.get(key)
    if state:
        storage.delete(state)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


def post_request():
    """Handles POST requests to create a new State object."""
    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()
    if 'name' not in body_request:
        abort(400, 'Missing name')

    new_state = State(**body_request)
    storage.new(new_state)
    storage.save()
    return jsonify(new_state.to_dict()), 201


def put_request(state_id):
    """Handles PUT requests to update an existing State object."""
    key = f'State.{state_id}'
    states = storage.all(State)
    state = states.get(key)
    if state is None:
        abort(404)

    if not request.is_json:
        abort(400, 'Not a JSON')

    body_request = request.get_json()
    for key, value in body_request.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(state, key, value)

    storage.save()
    return jsonify(state.to_dict()), 200
