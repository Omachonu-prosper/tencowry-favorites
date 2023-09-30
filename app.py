import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS


app = Flask(__name__)

load_dotenv()
CORS()

try:
    # If we are working in a production environment (deployed state)
    # the database to be used will be the mongodb atlas database
    # else the local mongodb instance will be used
    app_status = os.environ.get('APP_STATUS')
    if app_status == 'production':
        db_username = os.environ['DATABASE_USER']
        db_passwd = os.environ['DATABASE_PASSWORD']
        db_url = os.environ['DATABASE_URL']
        uri = f"mongodb+srv://{db_username}:{db_passwd}@{db_url}"
    else:
        uri = "mongodb://127.0.0.1:27017"
except Exception as e:
    print(f'Error in connection to Database: {e}')

client = MongoClient(uri)
db = client['test']
users = db['users']


@app.route('/user/favorites/add', strict_slashes=False, methods=['POST'])
def add_favorite():
    # Validate payload
    data = request.json
    product_id = data.get('product-id', None)

    if product_id is None:
        return jsonify({
            'message': 'Missing payload: product-id is required',
            'status': False
        }), 400    
    product_id = int(product_id)

    # Check for duplicates
    duplicate = users.find_one({'favorites': product_id})
    if duplicate:
        return jsonify({
            'message': 'Duplicate: product already added to favorites',
            'status': False
        }), 409
    
    # Add product to favorites
    add = users.update_one({'user_id': 'user-1'}, {'$push': {'favorites': product_id}})
    if add.modified_count:
        return jsonify({
            'message': 'Success: product added to favorites',
            'status': True
        }), 201
    else:
        return jsonify({
            'message': 'Failure: failed to add product to favorites',
            'status': False
        }), 422


@app.route('/user/favorites/remove/<int:product_id>', strict_slashes=False, methods=['DELETE'])
def delete_favorite(product_id):
    delete = users.update_one({"user_id": 'user-1'}, {'$pull': {'favorites': product_id}})
    if delete.modified_count:
        return jsonify({
            'message': 'Success: product removed from favorites',
            'status': True
        }), 200
    else:
        return jsonify({
            'message': 'Not found: product not in favorites',
            'status': False
        }), 404


@app.route('/user/favorites/all', strict_slashes=False)
def get_all_favorites():
    return 'Under construction'


@app.route('/', strict_slashes=False)
def index():
    return jsonify({
        'message': 'Tencowry Favorites',
        'status': True
    }), 200


if __name__ == '__main__':
    if os.environ.get('APP_STATUS') == 'production':
        app.run()
    else:
        app.run(debug=True)