import uuid

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
from database import db_connector as db
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import send_notification, send_alert, write_log

# Set up upload folder
UPLOAD_FOLDER = 'static/img/'
# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_mapping(SECRET_KEY='dev')
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


def process_price(raw_price):
    try:
        price = Decimal(raw_price)
        price = price.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        if len(str(price)) > 10:
            raise ValueError("Price too large")

        return price
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid start price")


# Route to display all listings
@app.route('/listings', methods=['GET'])
def get_listings():
    db_conn = db.connect_to_database()

    # Update the query to join the Listings, Photos, and Bids tables
    query = """
    SELECT 
        L.*,
        MAX(B.bidAmt) AS bidAmt,
        MAX(P.photoPath) AS photoPath,
        GROUP_CONCAT(C.label SEPARATOR ',') AS categories
    FROM 
        Listings L
    LEFT JOIN 
        Bids B ON L.bidID = B.bidID
    LEFT JOIN 
        Photos P ON L.listingID = P.listingID
    LEFT JOIN 
        ListingCategory LC ON L.listingID = LC.listingID
    LEFT JOIN 
        Categories C ON LC.categoryID = C.categoryID
    WHERE 
        L.userID IS NOT NULL AND L.status = 'active'
    GROUP BY 
        L.listingID;
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


@app.route('/flagged-listings', methods=['GET'])
def get_flagged_listings():
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
        Listings.userID IS NOT NULL AND Listings.status = 'active' AND Listings.numFlagged > 0
    ORDER BY Listings.endDate ASC;
        
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

    print(processed_listings)

    return jsonify({'success': True, 'data': processed_listings})


# Route for searching listings
@app.route('/search', methods=['POST'])
def search_listings():
    search_query = request.json['searchquery']
    db_conn = db.connect_to_database()
    query = """
    SELECT
       L.*,
       MAX(B.bidAmt) AS bidAmt,
       MAX(P.photoPath) AS photoPath,
       GROUP_CONCAT(C.label SEPARATOR ',') AS categories
    FROM Listings L
    LEFT JOIN Bids B ON L.bidID = B.bidID
    LEFT JOIN Photos P ON L.listingID = P.listingID
    LEFT JOIN ListingCategory LC ON L.listingID = LC.listingID
    LEFT JOIN Categories C ON LC.categoryID = C.categoryID
    WHERE L.userID IS NOT NULL AND L.status = 'active' 
    GROUP BY L.listingID
    HAVING L.name LIKE %s OR FIND_IN_SET(%s, GROUP_CONCAT(C.label)) > 0;
    """
    listings = db.execute_query(db_connection=db_conn, query=query, query_params=(f"%{search_query}%",search_query)).fetchall()
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


@app.route('/search-by-time', methods=['POST'])
def search_by_time():
    filterStartDate = request.json['filterStartDate']
    filterEndDate = request.json['filterEndDate']
    db_conn = db.connect_to_database()
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
        Listings.userID IS NOT NULL AND 
        Listings.status != 'active' AND
        Listings.endDate BETWEEN %s AND %s;
    """
    listings = db.execute_query(db_connection=db_conn, query=query,
                                query_params=(filterStartDate, filterEndDate)).fetchall()
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


@app.route('/search-by-category', methods=['POST'])
def search_by_category():
    category = request.json['category']

    db_conn = db.connect_to_database()
    query = "SELECT categoryID FROM Categories WHERE label = %s;"
    result = db.execute_query(
        db_connection=db_conn, query=query, query_params=category).fetchone()
    category_id = result['categoryID']

    query = """
    SELECT 
        L.*,
        P.photoPath,
        LC.categoryID,
        B.bidAmt
    FROM 
        Listings L
    JOIN 
        ListingCategory LC ON L.listingID = LC.listingID
    LEFT JOIN 
        Photos P ON L.listingID = P.listingID
    LEFT JOIN 
        Bids B ON L.bidID = B.bidID
    WHERE 
        L.userID IS NOT NULL
        AND L.status = 'active'
        AND LC.categoryID = %s;
    """
    listings = db.execute_query(db_connection=db_conn, query=query, query_params=(category_id)).fetchall()
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


@app.route('/submit-listing', methods=['POST'])
def submit_listing():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        # Use request.form for text fields

        name = request.form['name']
        userID = request.form['userID']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        startPrice = process_price(request.form['startPrice'])
        buyNowPrice = process_price(request.form['buyNowPrice'])
        description = request.form['description']
        quantity = request.form['quantity']
        shippingCosts = process_price(request.form['shippingCosts'])
        numFlagged = 0
        status = "inactive"

        if 'file' in request.files:
            photo = request.files['file']
        else:
            photo = None

        filepath = "./static/img/No_image_available.jpg"
        # generate the unique filename

        if photo and photo.filename != '':

            filepath = os.path.join("./"+app.config['UPLOAD_FOLDER'],str(uuid.uuid4())+'.jpg')
            photo.save(filepath)

        # Rest of the code remains the same
        query = "INSERT INTO Listings (name, userID, startDate, endDate, startPrice, buyNowPrice, " \
                "description, quantity, shippingCosts, numFlagged, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(name, userID, startDate, endDate, startPrice, buyNowPrice,
                                                              description, quantity, shippingCosts, numFlagged, status))
        list_id = cursor.lastrowid

        query = "INSERT INTO Photos (photoPath, listingID) VALUES (%s, %s);"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(filepath, list_id))

        # notify users who might be interested in this newly added item
        query = """
            SELECT
                DISTINCT u.email
            FROM
                 Users u
            JOIN
                Watchlists w ON u.userID = w.userID
            WHERE
                %s BETWEEN w.lowerPrice AND w.upperPrice
                AND %s LIKE CONCAT('%%', w.keyword, '%%');
        """

        email_listing = db.execute_query(db_connection=db_conn, query=query, query_params=(startPrice, name)).fetchall()
        for email_dict in email_listing:
            msg = "We found an item you might be interested in: {}".format(name)
            send_notification(email_dict['email'], msg)

        return jsonify({'success': True, 'listingID': list_id}), 200


@app.route('/update-listing', methods=['POST'])
def update_listing():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        name = data['name']
        buyNowPrice = process_price(data['buyNowPrice'])
        description = data['description']
        quantity = data['quantity']
        shippingCosts = process_price(data['shippingCosts'])

        query = """
        UPDATE Listings
        SET 
            name = %s,
            buyNowPrice = %s,
            description = %s,
            quantity = %s,
            shippingCosts = %s
        WHERE 
            listingID = %s;
        """
        db.execute_query(
            db_connection=db_conn, query=query,
            query_params=(name, buyNowPrice, description, quantity, shippingCosts, listingID))

        return jsonify({'success': True, 'message': "listing has been updated", 'listingID': listingID}), 200


@app.route('/end-listing', methods=['POST'])
def end_listing():
    db_conn = db.connect_to_database()
    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        
        # Change the endDate to the startDate in case the loop restore the staus to active
        query = "SELECT startDate FROM Listings WHERE listingID = %s;"
        result = db.execute_query(
            db_connection=db_conn, query=query, query_params=(listingID,)).fetchone()
        startDate = result['startDate']

        query = "UPDATE Listings SET status = 'hold', endDate = %s WHERE listingID = %s"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=(startDate, listingID))
        
        # query = "UPDATE Listings SET status = 'hold' WHERE listingID = %s"
        # db.execute_query(
        #     db_connection=db_conn, query=query, query_params=listingID)
        query = """
        SELECT
            L.listingID,
            B.userID,
            B.bidAmt
        FROM
            Listings L
        INNER JOIN
            Bids B ON L.bidID = B.bidID
        WHERE
            L.listingID = %s;
        """
        resultlist = db.execute_query(
            db_connection=db_conn, query=query, query_params=listingID).fetchall()
        result = resultlist[0]
        userID = result['userID']
        listingID = result['listingID']
        bidAmt = process_price(result['bidAmt'])

        query = "INSERT INTO ShoppingcartRecords (userID, listingID, dealPrice) VALUES (%s, %s, %s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(userID, listingID, bidAmt))
        record_id = cursor.lastrowid;
        print("The listing ", listingID, " has been placed on hold, shopping cart record ", record_id,
              " has been created.")
        return jsonify({'success': True, 'message': "shopping cart created"}), 200


@app.route('/get-shoppingcart', methods=['POST'])
def get_shoppingcart():
    userID = request.json['userID']
    db_conn = db.connect_to_database()
    query = """
    SELECT 
        sc.shoppingcartRecordID,
        sc.listingID, 
        l.name, 
        l.endDate,
        sc.dealPrice, 
        l.shippingCosts, 
        l.quantity, 
        l.description
    FROM 
        shoppingcartRecords sc
    JOIN 
        Listings l ON sc.listingID = l.listingID
    WHERE 
        sc.userID = %s;
    """
    listings = db.execute_query(db_connection=db_conn, query=query, query_params=(userID)).fetchall()
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
    return jsonify({'success': True, 'data': processed_listings}), 200


@app.route('/terminate-listing', methods=['POST'])
def terminate_listing():
    db_conn = db.connect_to_database()
    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        
        # Change the endDate to the startDate in case the loop restore the staus to active
        query = "SELECT startDate FROM Listings WHERE listingID = %s;"
        result = db.execute_query(
            db_connection=db_conn, query=query, query_params=(listingID,)).fetchone()
        startDate = result['startDate']
        
        query = "SELECT bidID FROM Listings WHERE listingID = %s"
        result = db.execute_query(
            db_connection=db_conn, query=query, query_params=listingID).fetchone()
        bidID = result['bidID']
        if bidID:
            return jsonify({'success': False, 'message': "listing has bid"}), 400
        query = "UPDATE Listings SET status = 'inactive', endDate = %s WHERE listingID = %s"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=(startDate, listingID))
        return jsonify({'success': True, 'message': "listing is inactive"}), 200


@app.route('/checkout', methods=['POST'])
def checkout_listing():
    db_conn = db.connect_to_database()
    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        query = "UPDATE Listings SET status = 'inactive' WHERE listingID = %s"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=listingID)
        query = "DELETE FROM shoppingcartRecords WHERE listingID = %s;"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=listingID)
        return jsonify({'success': True, 'message': "listing is paid and removed from shopping cart"}), 200


@app.route('/flag-listing', methods=['POST'])
def flag_listing():
    db_conn = db.connect_to_database()
    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        query = "UPDATE Listings SET numFlagged = numFlagged+1 WHERE listingID = %s"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=listingID)
        return jsonify({'success': True, 'message': "listing is flagged as counterfeit"}), 200


@app.route('/add-category', methods=['POST'])
def add_category():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        data = request.json
        new_category = data['new_category']

        query = "INSERT INTO Categories (label) VALUES (%s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=new_category)
        category_id = cursor.lastrowid

        return jsonify({'success': True, 'category_id': category_id}), 200


@app.route('/remove-category', methods=['POST'])
def remove_category():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        data = request.json
        category = data['category']

        query = "SELECT categoryID FROM Categories WHERE label = %s"
        result = db.execute_query(
            db_connection=db_conn, query=query, query_params=category).fetchone()
        category_id = result['categoryID']

        query = "DELETE FROM ListingCategory WHERE categoryID = %s;"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=category_id)

        query = "DELETE FROM Categories WHERE categoryID = %s;"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=category_id)

        return jsonify({'success': True, 'message': "category has been removed"}), 200


@app.route('/categorize-listing', methods=['POST'])
def categorize_listing():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        data = request.json
        listingID = data['listingID']
        category = data['category']

        query = "SELECT categoryID FROM Categories WHERE label = %s;"
        result = db.execute_query(
            db_connection=db_conn, query=query, query_params=category).fetchone()
        category_id = result['categoryID']
        query = "INSERT INTO ListingCategory (listingID, categoryID) VALUES (%s, %s);"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=(listingID, category_id))

        return jsonify({'success': True, 'message': "your item has been categorized"}), 200


@app.route('/add-watchlist', methods=['POST'])
def add_watchlist():
    db_conn = db.connect_to_database()

    if request.method == 'POST':
        data = request.json
        userID = data['userID']
        keyword = data['keyword']
        lowerPrice = process_price(data['lowerPrice'])
        upperPrice = process_price(data['upperPrice'])

        query = "INSERT INTO Watchlists (userID, lowerPrice, upperPrice, keyword) VALUES (%s, %s, %s, %s);"
        db.execute_query(
            db_connection=db_conn, query=query, query_params=(userID, lowerPrice, upperPrice, keyword))

        return jsonify({'success': True, 'message': "a watchlist has been created"}), 200


@app.route('/get-watchlist', methods=['POST'])
def get_watchlist():
    userID = request.json['userID']
    db_conn = db.connect_to_database()
    query = """
    SELECT * FROM watchlists where userID = %s;
    """
    listings = db.execute_query(db_connection=db_conn, query=query, query_params=(userID)).fetchall()
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
    return jsonify({'success': True, 'data': processed_listings}), 200


# Run listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9991))
    app.run(port=port, debug=True, host='0.0.0.0')
