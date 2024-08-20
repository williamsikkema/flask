from flask import Flask, request, jsonify
import threading
import time
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Global variables to store the timer and the remaining time
timer = None
lock = threading.Lock()
remaining_time = 0

# Set up the timezone for Pacific Time
pacific = pytz.timezone('America/Los_Angeles')

def start_timer():
    global timer, remaining_time
    with lock:  # Ensure only one thread can modify the timer at a time
        # Get the current time in Pacific Time
        current_time = datetime.now(pacific)
        current_hour = current_time.hour

        # Check if it's between 9 AM and 5 PM Pacific Time
        if 9 <= current_hour < 17:
            remaining_time = 2700  # 2700 seconds = 45 minutes
        else:
            remaining_time = 10  # 10 seconds

        if timer:
            timer.cancel()  # Cancel the previous timer
        timer = threading.Timer(remaining_time, send_webhook)
        timer.start()

        # Start a thread to update the remaining time
        threading.Thread(target=update_remaining_time).start()

def update_remaining_time():
    global remaining_time
    while remaining_time > 0:
        time.sleep(1)
        with lock:
            remaining_time -= 1

        # Check if it's 5 PM exactly and adjust the timer to 15 seconds if needed
        current_time = datetime.now(pacific)
        if current_time.hour == 17 and current_time.minute == 0 and remaining_time > 15:
            with lock:
                remaining_time = 15
                print("Timer adjusted to 15 seconds at 5 PM")
                timer.cancel()
                timer = threading.Timer(remaining_time, send_webhook)
                timer.start()

def send_webhook():
    url = f"https://maker.ifttt.com/trigger/lock/with/key/byTC_tHcJHvGsv7cPhRX4HZACfNSDFahFMgJxaPN6_h"
    response = requests.post(url)
    print(f"Webhook sent with status code: {response.status_code}")

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        # Attempt to get JSON data, but don't raise an error if it's not present
        data = request.get_json(silent=True)
        
        if data is None:
            print("No JSON data received")
        else:
            print(f"Received webhook with data: {data}")
        
        # Start the timer regardless of whether JSON data was received
        start_timer()
        
        return "Webhook received and timer started/restarted", 200
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/time_remaining', methods=['GET'])
def get_time_remaining():
    with lock:
        return jsonify({"time_remaining": remaining_time}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)