from flask import Flask, jsonify, request
import smtplib
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')
CORS(app)  # Enable CORS

sender_email = "javasavesus@gmail.com"
password = "nlvjfxxadekmlzgu"


# Route for notice email
@app.route('/notice', methods=['POST'])
def notice():
    """
    send notification to receiver
    """
    try:
        receiver_email = request.json['receiver']
        message = request.json['msg']
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, password)

        msg = MIMEMultipart()
        msg['From'] = 'JavaSavesUs Auction'
        msg['To'] = receiver_email
        msg['Subject'] = 'Notice'
        msg.attach(MIMEText(message, 'plain'))
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        return jsonify({'success': True, 'error': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for alert email
@app.route('/alert', methods=['POST'])
def alert():
    """
    send altert to receiver
    """
    try:
        receiver_email = request.json['receiver']
        message = request.json['msg']
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, password)

        msg = MIMEMultipart()
        msg['From'] = 'JavaSavesUs Auction'
        msg['To'] = receiver_email
        msg['Subject'] = '!!!Alert!!!'
        msg.attach(MIMEText(message, 'plain'))
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        return jsonify({'success': True, 'error': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Run listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9993))
    app.run(port=port, debug=True, host='0.0.0.0')
