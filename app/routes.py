from flask import Blueprint, request, jsonify, current_app
from getmac import get_mac_address
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import time
from flask_cors import cross_origin
import sqlitecloud

api_bp = Blueprint('api', __name__)

# SQLite Cloud connection
conn = sqlitecloud.connect("sqlitecloud://cnwui0evhz.g5.sqlite.cloud:8860/my-database?apikey=ee6Lm9tAV07WnebyuftsY4g5dMYDCVxWLaneQoWScww")

def hash_mac_address(mac_address):
    return hashlib.sha256(mac_address.encode()).hexdigest()

def execute_query(query, params=None):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None

@api_bp.route('/', methods=['GET'])
@cross_origin()
def home():
    return jsonify({'message': 'Welcome to the Flask API!'})

@api_bp.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    existing_user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
    if existing_user:
        return jsonify({'message': 'Username already taken. Please choose another one.'}), 400

    mac_address = get_mac_address()
    if not mac_address:
        return jsonify({'message': 'Unable to retrieve MAC address.'}), 400

    hashed_mac = hash_mac_address(mac_address)
    hashed_password = generate_password_hash(password)

    execute_query('INSERT INTO users (username, password, mac_address) VALUES (?, ?, ?)', (username, hashed_password, hashed_mac))
    return jsonify({'message': 'Registration successful! Please log in.'}), 201

@api_bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_mac_address = get_mac_address()

    hashed_mac_address = hash_mac_address(user_mac_address)

    user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
    if user:
        stored_password = user[0]['password']
        stored_mac_address = user[0]['mac_address']

        if check_password_hash(stored_password, password):
            if stored_mac_address == hashed_mac_address:
                return jsonify({'message': 'Login successful!'}), 200
            else:
                return jsonify({'message': 'MAC address does not match.'}), 403
        else:
            return jsonify({'message': 'Incorrect password.'}), 401
    else:
        return jsonify({'message': 'Username not found.'}), 404
