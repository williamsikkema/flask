from flask import Flask, request
import threading
import time
import requests

app = Flask(__name__)

# Global variable to store the timer
timer = None
lock = threading.Lock()

def start_timer():
    global timer
    with lock:  # Ensure only one thread can modify the timer at a time
        if timer:
            timer.cancel()  # Cancel the previous timer
        timer = threading.Timer(1800, send_webhook)  # 1800 seconds = 30 minutes
        timer.start()

def send_webhook():
    url = f"https://maker.ifttt.com/trigger/lock/with/key/byTC_tHcJHvGsv7cPhRX4HZACfNSDFahFMgJxaPN6_h"
    response = requests.post(url)
    print(f"Webhook sent with status code: {response.status_code}")

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()  # You can also handle specific data if needed
    print(f"Received webhook with data: {data}")
    start_timer()
    return "Webhook received and timer started/restarted", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

