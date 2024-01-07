import requests

LOG_SERVICE_URL = "http://localhost:9992/log"
NOTICE_SERVICE_URL = "http://localhost:9993/notice"
ALERT_SERVICE_URL = "http://localhost:9993/alert"
HEADERS = {"Content-Type": "application/json"}


def write_log(msg):
    payload = {"msg": msg}
    response = requests.post(LOG_SERVICE_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return True
    else:
        return False


def send_notification(receiver, msg):
    payload = {"msg": msg, "receiver": receiver}
    response = requests.post(NOTICE_SERVICE_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("notification sent successful!")
        print("Response content:", response.content.decode())
        #write_log(f"Send notice to {receiver} success! Message: {msg}")
    else:
        print("notification failed with status code:", response.status_code)
        #write_log(f"Send notice to {receiver} failed. Code: {response.status_code}")


def send_alert(receiver, msg):
    payload = {"msg": msg, "receiver": receiver}
    response = requests.post(ALERT_SERVICE_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("Alert sent successful!")
        print("Response content:", response.content.decode())
        #write_log(f"Send alert to {receiver} success! Message: {msg}")
    else:
        print("Alert failed with status code:", response.status_code)
        #write_log(f"Send alert to {receiver} failed. Code: {response.status_code}")


if __name__ == "__main__":
    send_notification("tisonwang@uchicago.edu", "test_notification")
    send_alert("tisonwang@uchicago.edu", "test_alert")
