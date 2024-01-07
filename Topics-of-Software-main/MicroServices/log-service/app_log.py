from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import os


# Initialize Flask app
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')
CORS(app)  # Enable CORS

client = MongoClient()
db = client.auction_logs
log_collection = db.log


# Route for log writer
@app.route('/log', methods=['POST'])
def log():
    """
    Log message to MongoDB log
    """
    message = request.json['msg']

    entry = {}
    entry['timestamp'] = datetime.datetime.utcnow()
    entry['msg'] = message
    log_collection.insert_one(entry)
    return jsonify({'success': True})


# Route for log reader
@app.route('/logReader', methods=['GET'])
def logReader():
    """
    Check log from DB
    """
    documents = log_collection.find()
    logs = [document['timestamp'].strftime("%Y-%m-%d_%H:%M:%S") + ": " + document['msg']
            for document in documents]
    print(logs)
    return jsonify({'success': True, 'log': logs})


# Run listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9992))
    app.run(port=port, debug=True, host='0.0.0.0')
