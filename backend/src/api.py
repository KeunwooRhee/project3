import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    
    drink_list = Drink.query.all()
    print(drink_list)
    drinks = []
    for drink in drink_list:
        drinks.append(drink.short())
    
    return jsonify({
        "success": True, 
        "drinks": drinks
    }), 200
    '''
    drinks = Drink.short()

    return jsonify({
        "success": True, 
        "drinks": drinks
    }), 200
    '''
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drink_list = Drink.query.all()
    drinks = []
    for drink in drink_list:
        drinks.append(drink.long())

    return jsonify({
        "success": True, 
        "drinks": drinks
    }), 200
    
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    requests = request.get_json()

    title = requests['title']
    recipe = json.dumps(requests['recipe'])
   #print(title)
    #print(recipe)
    #print(type(title))
    #print(type(recipe))
    '''
    #[{'color': string, 'name':string, 'parts':number}]

    
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)
    '''

    new_drink = Drink(title = title, recipe = recipe)
    new_drink.insert()

    drink = new_drink.long()
    #print(drink)

    return jsonify({
        "success": True, 
        "drinks": drink
    }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    print(type(drink_id))
    updated_drink = Drink.query.filter_by(id=drink_id).one_or_none()
    print(updated_drink)
    if updated_drink is None:
        abort(404)
    
    requests = request.get_json()
    
    updated_drink.title = requests['title']
    updated_drink.recipe = json.dumps(requests['recipe'])

    #print(title)
    #print(recipe)

    updated_drink.update()

    drink = [updated_drink.long()]

    return jsonify({
        "success": True, 
        "drinks": drink
    }), 200


    #print(title)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    #print(drink_id)
    deleted_drink = Drink.query.filter_by(id=drink_id).one_or_none()
    #print(id)
    if deleted_drink is None:
        abort(404)

    deleted_drink.delete()
    id = drink_id

    return jsonify({
        "success": True, 
        "delete": id
    }), 200

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
    