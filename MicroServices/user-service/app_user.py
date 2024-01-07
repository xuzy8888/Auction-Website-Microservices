from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import database.db_connector as db
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from datetime import datetime

# Set up upload folder
UPLOAD_FOLDER = 'static/img/'

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_mapping(SECRET_KEY='dev')
CORS(app)  # Enable CORS

# Route to display all listings
@app.route('/listings', methods=['GET'])
def get_listings():
    db_conn = db.connect_to_database()

    # Update the query to join the Listings, Photos, and Bids tables
    query = """
    SELECT 
        Listings.*, 
        Photos.photoPath,
        Bids.bidAmt
    FROM 
        Listings 
    LEFT JOIN 
        Photos ON Listings.listingID = Photos.listingID
    LEFT JOIN 
        Bids ON Listings.bidID = Bids.bidID
    WHERE 
        Listings.userID IS NOT NULL AND Listings.endDate >= NOW();
    """

    listings = db.execute_query(db_connection=db_conn, query=query).fetchall()

    processed_listings = []
    for listing in listings:
        processed_listing = {}
        for key, value in listing.items():
            if isinstance(value, Decimal):
                processed_listing[key] = str(value)
            elif isinstance(value, datetime):
                processed_listing[key] = value.strftime('%Y-%m-%d %H:%M')
            else:
                processed_listing[key] = value
        processed_listings.append(processed_listing)
    return jsonify({'success': True, 'data': processed_listings})


# Route for searching listings
@app.route('/search', methods=['POST'])
def search_listings():
    search_query = request.json['searchquery']
    db_conn = db.connect_to_database()
    query = "SELECT * FROM Listings WHERE name LIKE %s AND userID IS NOT NULL AND endDate >= NOW();"
    listings = db.execute_query(db_connection=db_conn, query=query, query_params=(f"%{search_query}%",)).fetchall()
    return jsonify({'success': True, 'data': listings})


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    confirm_password = data['confirm_password']
    fname = data['fname']
    lname = data['lname']
    email = data['email']
    rating = calculate_initial_rating(username, password, email)

    db_conn = db.connect_to_database()
    error = None

    if not username or not password or not confirm_password:
        error = 'Username and Password are required.'
    elif password != confirm_password:
        error = 'Passwords do not match.'
    elif db.execute_query(
        db_conn,
        'SELECT userID FROM Users WHERE userName = %s', (username,)
    ).fetchone() is not None:
        error = 'User already registered.'

    if error:
        return jsonify({'success': False, 'error': error}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    date_joined = date.today().strftime("%Y-%m-%d")
    isActive = True
    isAdmin = False

    db.execute_query(
        db_conn,
        'INSERT INTO Users (userName, password, firstName, lastName, email, dateJoined, rating, isActive, isAdmin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (username, hashed_password, fname, lname, email, date_joined, rating, isActive, isAdmin)
    )

    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

def calculate_initial_rating(username, password, email):
    rating = 3.0  # Start with a base rating
    
    # Increment based on username length; longer usernames get a higher increment
    username_length_increment = min(0.25 * (len(username) // 2 - 2), 1.0)
    rating += username_length_increment

    # Increment based on password complexity
    complexity_increment = 0.0
    if any(char.isdigit() for char in password):
        complexity_increment += 0.25
    if any(not char.isalnum() for char in password):
        complexity_increment += 0.25
    if len(password) >= 8:
        complexity_increment += 0.5
    rating += complexity_increment

    # Increment based on email domain
    email_domain = email.split('@')[-1].lower()
    if email_domain in ['edu', 'org', 'gov']:
        rating += 0.25
    elif email_domain.endswith('.com'):
        rating += 0.1

    return min(rating, 5.0)



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    db_conn = db.connect_to_database()
    user = db.execute_query(
        db_conn,
        'SELECT * FROM Users WHERE userName = %s AND isActive = TRUE', (username,)
    ).fetchone()

    if user and check_password_hash(user['password'], password):

        return jsonify({'success': True, 'user': {'username': user['userName'], 'email': user['email'], 'id': user['userID'], 'isAdmin': user['isAdmin']}})

    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401


@app.route('/user/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    db_conn = db.connect_to_database()
    user_query = "SELECT * FROM Users WHERE userID = %s;"
    user = db.execute_query(db_connection=db_conn, query=user_query, query_params=(user_id,)).fetchone()


    processed_listing = {}
    for key, value in user.items():
        if isinstance(value, Decimal):
            processed_listing[key] = str(value)
        elif isinstance(value, datetime):
            processed_listing[key] = value.strftime('%Y-%m-%d %H:%M')
        else:
            processed_listing[key] = value

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({'success': True, 'data': processed_listing})


@app.route('/user/<int:user_id>/active-listings', methods=['GET'])
def get_active_listings(user_id):
    # print(f"get_active_listings called with user_id: {user_id}")
    db_conn = db.connect_to_database()

    # First, check if the user is an admin
    admin_check_query = "SELECT isAdmin FROM Users WHERE userID = %s"
    is_admin = db.execute_query(db_connection=db_conn, query=admin_check_query, query_params=(user_id,)).fetchone()

    # Decide the query based on the admin status
    if is_admin and is_admin['isAdmin']:
        listings_query = """
        SELECT 
            Listings.*, 
            Photos.photoPath,
            Bids.bidAmt
        FROM 
            Listings 
        LEFT JOIN 
            Photos ON Listings.listingID = Photos.listingID
        LEFT JOIN 
            Bids ON Listings.bidID = Bids.bidID
        WHERE 
            Listings.status = 'active';
        """
        query_params = ()
    else:
        listings_query = """
        SELECT 
            Listings.*, 
            Photos.photoPath,
            Bids.bidAmt
        FROM 
            Listings 
        LEFT JOIN 
            Photos ON Listings.listingID = Photos.listingID
        LEFT JOIN 
            Bids ON Listings.bidID = Bids.bidID
        WHERE 
            Listings.userID = %s AND Listings.status = 'active';
        """
        query_params = (user_id,)

    listings = db.execute_query(db_connection=db_conn, query=listings_query, query_params=query_params).fetchall()

    processed_listings = []
    for listing in listings:
        processed_listing = {}
        for key, value in listing.items():
            if isinstance(value, Decimal):
                processed_listing[key] = str(value)
            elif isinstance(value, datetime):
                processed_listing[key] = value.strftime('%Y-%m-%d %H:%M')
            else:
                processed_listing[key] = value
        processed_listings.append(processed_listing)

    return jsonify({'success': True, 'data': processed_listings})


@app.route('/user/<int:user_id>/active-users', methods=['GET'])
def get_active_users(user_id):
    print(f"get_active_users called with user_id: {user_id}")
    db_conn = db.connect_to_database()

    # First, check if the user is an admin
    admin_check_query = "SELECT isAdmin FROM Users WHERE userID = %s"
    is_admin = db.execute_query(db_connection=db_conn, query=admin_check_query, query_params=(user_id,)).fetchone()

    # If the current user is not an admin, return an error response
    if is_admin['isAdmin']:
        users_query = """
        SELECT 
            userID, userName, firstName, lastName, email, dateJoined, rating, isActive
        FROM 
            Users
        WHERE 
            isAdmin = FALSE AND isActive = TRUE;
        """

        users = db.execute_query(db_connection=db_conn, query=users_query).fetchall()
        #return jsonify({'success': False, 'message': 'Access denied'}), 403
    else:
    # If the current user is an admin, fetch all active non-admin users
        users_query = """
        SELECT 
            userID, userName, firstName, lastName, email, dateJoined, rating, isActive
        FROM 
            Users
        WHERE 
            userID = %s;
        """

        users = db.execute_query(db_connection=db_conn, query=users_query, query_params=user_id).fetchall()

    processed_users = []
    for user in users:
        processed_user = {}
        for key, value in user.items():
            if isinstance(value, Decimal):
                processed_user[key] = str(value)
            elif isinstance(value, datetime):
                processed_user[key] = value.strftime('%Y-%m-%d %H:%M')
            else:
                processed_user[key] = value
        processed_users.append(processed_user)

    return jsonify({'success': True, 'data': processed_users})

@app.route('/suspend-user', methods=['POST'])
def suspend_user():
    db_conn = db.connect_to_database()
    user_id = request.json['user_id']
    
    # Check if the user exists
    user_check_query = "SELECT * FROM Users WHERE userID = %s"
    user = db.execute_query(db_connection=db_conn, query=user_check_query, query_params=(user_id,)).fetchone()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    # Update the isActive field for the user to False (inactive)
    suspend_query = "UPDATE Users SET isActive = FALSE WHERE userID = %s"
    db.execute_query(db_connection=db_conn, query=suspend_query, query_params=(user_id,))
    
    return jsonify({'success': True, 'message': f'User {user_id} suspended successfully'}), 200


@app.route('/user/<int:user_id>/bid-history', methods=['GET'])
def get_bid_history(user_id):
    db_conn = db.connect_to_database()
    bid_history_query = """
    SELECT 
        Bids.*, 
        Listings.name 
    FROM 
        Bids 
    JOIN 
        Listings ON Bids.listingID = Listings.listingID
    WHERE 
        Bids.userID = %s;
    """
    bid_history = db.execute_query(db_connection=db_conn, query=bid_history_query, query_params=(user_id,)).fetchall()

    processed_listings = []
    for listing in bid_history:
        processed_listing = {}
        for key, value in listing.items():
            if isinstance(value, Decimal):
                processed_listing[key] = str(value)
            elif isinstance(value, datetime):
                processed_listing[key] = value.strftime('%Y-%m-%d %H:%M')
            else:
                processed_listing[key] = value
        processed_listings.append(processed_listing)

    return jsonify({'success': True, 'data': processed_listings})



# Run listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9990))
    app.run(port=port, debug=True, host='0.0.0.0')
