from decimal import ROUND_DOWN, Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, g, url_for, flash,jsonify
import os
import database.db_connector as db
from flask_cors import CORS
# from datetime import date
from werkzeug.utils import secure_filename
from validation import validate_new_listing, validate_photo, validate_bid
import threading
# from datetime import datetime
import datetime
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import send_notification, send_alert, write_log
import requests

# Set up upload folder
UPLOAD_FOLDER = 'static/img/'

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_mapping(SECRET_KEY='dev')
CORS(app)  # Enable CORS

# The function for keep looping and check the status of the listings
def update_listing_status():
    while True:
        current_time = datetime.datetime.now()
        db_conn = db.connect_to_database()

        # Update listings to 'active' if current time is equal to startDate
        update_query = """
        UPDATE Listings 
        SET status = 'active' 
        WHERE startDate <= %s AND endDate > %s AND status != 'active';
        """
        db.execute_query(db_connection=db_conn, query=update_query, query_params=(current_time, current_time))

        # Update listings to 'hold' if current time is greater than or equal to endDate
        update_query = """
        SELECT listingID 
        from Listings 
        WHERE endDate <= %s AND status = 'active';
        """
        ended_listings = db.execute_query(db_connection=db_conn, query=update_query, query_params=(current_time,)).fetchall()
        for listing in ended_listings:
            listingID = listing['listingID']
            url = 'http://localhost:9991/end-listing'  # Replace with your target URL
            data = {
                'listingID': listingID
            }
            headers = {
                'Content-Type': 'application/json'  # Example header
            }
            response = requests.post(url, json=data, headers=headers)

            # To check if the request was successful
            if response.status_code == 200:
                print("Success:", response.json())
            else:
                print("Error:", response.status_code, response.text)

        
        # Update countdown for active listings
        update_query = """
        UPDATE Listings 
        SET countDown = TIMESTAMPDIFF(SECOND, %s, endDate) 
        WHERE endDate > %s AND status = 'active';
        """
        db.execute_query(db_connection=db_conn, query=update_query, query_params=(current_time, current_time))

        # Sleep for 1 second before the next check, maybe we can change to 60s
        time.sleep(1)

# Start the thread
update_thread = threading.Thread(target=update_listing_status)
update_thread.start()

def process_price(raw_price):
    try:
        price = Decimal(raw_price)
        price = price.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        if len(str(price)) > 10:
            raise ValueError("Price too large")

        return price
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid start price")

@app.route('/place-bid/<int:list_id>', methods=['POST'])
def place_bid(list_id):
        data = request.get_json()
        user_id = data['userID']
        bid_amt = process_price(data['bidAmt'])
        bid_date = datetime.date.today()
        db_conn = db.connect_to_database()

        # Check if the current bid highest
        query = "SELECT l.listingID, l.bidID, l.startPrice as startPrice, b.bidAmt as amount FROM Listings l LEFT JOIN Bids b ON l.bidID = b.bidID WHERE l.listingID = %s;"
        high_bid = db.execute_query(db_connection=db_conn, query=query,
                                    query_params=(list_id,)).fetchone()

        valid_bid, message = validate_bid(bid_amt, high_bid)

        # Find the email of the seller 
        query = """
        SELECT u.email as email
        From Users u LEFT JOIN Listings l ON u.userID = l.userID
        WHERE l.listingID = %s;
        """
        sellerEmail = db.execute_query(db_connection=db_conn, query=query,
                                    query_params=(list_id,)).fetchone()
        
        # Find current highest buyer email
        query = """
        SELECT u.email as email
        From Users u LEFT JOIN Bids b ON u.userID = b.userID
        LEFT JOIN Listings l ON b.bidID = l.bidID
        WHERE l.listingID = %s;
        """
        buyerEmail = db.execute_query(db_connection=db_conn, query=query,
                                    query_params=(list_id,)).fetchone()

        if not valid_bid:
            flash(message, 'danger')
            return jsonify({'success': False, "message": "invalid bid"}), 400
        else:
            query = "INSERT INTO Bids (userID, listingID, bidAmt, bidDate) VALUES (%s, %s, %s, %s)"
            cursor = db.execute_query(db_connection=db_conn, query=query,
                                      query_params=(user_id, list_id,
                                                    bid_amt, bid_date))
            bid_id = cursor.lastrowid

            query = "UPDATE Listings SET bidID = %s WHERE listingID = %s;"
            db.execute_query(db_connection=db_conn, query=query,
                            query_params=(bid_id, list_id))
            
            # send alerts to seller and former buyer
            if sellerEmail:
                send_alert(sellerEmail['email'], "Someone has placed a bid on your listing.")
            if buyerEmail:
                send_alert(buyerEmail['email'], "Someone has placed a higher bid than you!")

            flash(message, 'success')
            return jsonify({'success': True, "message": "your bid has been placed"}), 200


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9113))
    app.run(port=port, debug=True)
