from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

# Global variables to store the timer and the remaining time
timer = None
lock = threading.Lock()
remaining_time = 0

def start_timer():
    global timer, remaining_time
    with lock:  # Ensure only one thread can modify the timer at a time
        if timer:
            timer.cancel()  # Cancel the previous timer
        remaining_time = 1800  # 1800 seconds = 30 minutes
        timer = threading.Timer(1800, send_webhook)  # 1800 seconds = 30 minutes
        timer.start()

        # Start a thread to update the remaining time
        threading.Thread(target=update_remaining_time).start()

def update_remaining_time():
    global remaining_time
    while remaining_time > 0:
        time.sleep(1)
        with lock:
            remaining_time -= 1

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
