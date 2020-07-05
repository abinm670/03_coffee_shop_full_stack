import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS


from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import pprint

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Headers',
                         'GET,PUT,POST,DELETE,OPTIONS')

    return response


db_drop_and_create_all()

# ROUTES


@app.route('/')
def index():
    return jsonify({
        "success": True,
        "message": "welocme to udacity coffee shop"
    })


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    return jsonify({"success": True, "drinks": [i.short() for i in drinks]})


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    if drinks:
        data = [drink.long() for drink in drinks]

    return jsonify({"success": True, "drinks": data})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    
        info = request.get_json()
        title = info.get('title')
        recipe = json.dumps(info.get('recipe'))

        if 'title' and 'recipe' not in info:
            abort(422)

        try:
            drink = Drink(title=title, recipe=recipe)
            drink.insert()
            print([drink.long()])

            return jsonify({
                'success': True,
                'drinks': drink.long()
            })
        except:
            abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_menu(jwt, drink_id):

    data = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if 'title' not in data:
        abort(422)

    drink.title = data['title']
    drink.update()

    return jsonify({
        'sucess': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    # print(jwt)
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        "delete": id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(AuthError)
def handle_auth_errors(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    }), 401

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }, 422)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }, 404)



@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }, 500)






