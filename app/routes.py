from flask import Blueprint, request, jsonify, current_app
from .models import db, User
from getmac import get_mac_address
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import time
from sqlalchemy.exc import OperationalError
from flask_cors import cross_origin  # Import the decorator

api_bp = Blueprint('api', __name__)

def hash_mac_address(mac_address):
    """Helper function to hash the MAC address."""
    return hashlib.sha256(mac_address.encode()).hexdigest()

# Function to handle retry in case of SQLite locking error
def commit_with_retry():
    retries = 3  # Set the number of retries
    for _ in range(retries):
        try:
            db.session.commit()
            return
        except OperationalError as e:
            if 'database is locked' in str(e):
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                raise  # Reraise the error if it's not a database locking error
    db.session.rollback()  # If retry limit reached, rollback
    raise Exception('Failed to commit after retries due to database being locked.')

# Register route with CORS
@api_bp.route('/register', methods=['POST'])
@cross_origin()  # Allow CORS for this route
def register():
    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    password = data.get('password')

    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already taken. Please choose another one.'}), 400

    # Automatically fetch the system's MAC address
    mac_address = get_mac_address()
    if not mac_address:
        return jsonify({'message': 'Unable to retrieve MAC address.'}), 400

    # Hash the MAC address for secure storage
    hashed_mac = hash_mac_address(mac_address)

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    # Create and store the new user with hashed MAC address and hashed password
    new_user = User(username=username, password=hashed_password, mac_address=hashed_mac)
    db.session.add(new_user)
    
    try:
        commit_with_retry()  # Commit to the database with retry logic
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

    return jsonify({'message': 'Registration successful! Please log in.'}), 201

# Login route with CORS
@api_bp.route('/login', methods=['POST'])
@cross_origin()  # Allow CORS for this route
def login():
    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    password = data.get('password')
    user_mac_address = get_mac_address()  # Get the MAC address of the client machine

    # Hash the user's MAC address for comparison
    hashed_mac_address = hash_mac_address(user_mac_address)

    # Query database for the user
    user = User.query.filter_by(username=username).first()
    if user:
        # Verify if the entered password matches the stored one
        if check_password_hash(user.password, password):  # Use hashed password comparison
            # Verify if the entered MAC address (hashed) matches the stored one
            if user.mac_address == hashed_mac_address:
                return jsonify({'message': 'Login successful!'}), 200
            else:
                return jsonify({'message': 'MAC address does not match.'}), 403
        else:
            return jsonify({'message': 'Incorrect password.'}), 401
    else:
        return jsonify({'message': 'Username not found.'}), 404

# Sample success routes for testing
@api_bp.route('/success', methods=['GET'])
@cross_origin()  # Allow CORS for this route
def success():
    return jsonify({'message': 'Login successful'}), 200

@api_bp.route('/unauthorized', methods=['GET'])
@cross_origin()  # Allow CORS for this route
def unauthorized():
    return jsonify({'message': 'Unauthorized access'}), 403

@api_bp.route('/wrong_credentials', methods=['GET'])
@cross_origin()  # Allow CORS for this route
def wrong_credentials():
    return jsonify({'message': 'Wrong credentials'}), 401
