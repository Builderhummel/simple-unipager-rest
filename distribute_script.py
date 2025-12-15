import time
import threading
import json
import websocket
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import requests
from threading import Timer

app = Flask(__name__)

# Configuration
PASSWORD = "your_password"
WS_ENDPOINTS = ["ws://192.168.188.21:8055", "ws://192.168.188.22:8055", "ws://localhost:8055"]  # Add more as needed
T_DELAY = 5.0  # Delay in seconds between sends

# Global variables
transmission_history = []
MAX_HISTORY = 20
transmitting_status = {endpoint: False for endpoint in WS_ENDPOINTS}
availability_status = {endpoint: False for endpoint in WS_ENDPOINTS}
previous_transmitting_status = {endpoint: False for endpoint in WS_ENDPOINTS}
in_transmission = False

def send_to_ws(endpoint, ric, msg, m_type, m_func):
    try:
        ws = websocket.create_connection(endpoint)
        #ws.send(json.dumps({"Authenticate": PASSWORD}))
        payload = {
            "SendMessage": {
                "addr": ric,
                "data": msg,
                "mtype": m_type,
                "func": m_func
            }
        }
        ws.send(json.dumps(payload))
        ws.close()
    except Exception as e:
        print(f"Error sending to {endpoint}: {e}")

def check_available():
    for endpoint in WS_ENDPOINTS:
        try:
            ip = endpoint.split('://')[1].split(':')[0]
            response = requests.get(f'http://{ip}:8073/status.json', timeout=2)
            if response.status_code == 200:
                availability_status[endpoint] = True
            else:
                availability_status[endpoint] = False
        except Exception:
            availability_status[endpoint] = False
    # Schedule next check
    Timer(5.0, check_available).start()

# Start the availability check
check_available()

def dispatch_message(ric, msg, m_type, m_func):
    global in_transmission
    if in_transmission:
        return  # Prevent overlapping transmissions

    """Send message to all available transmitters with delay between sends"""
    # Get current availability status
    current_availability = {endpoint: availability_status[endpoint] for endpoint in WS_ENDPOINTS}

    in_transmission = True
    # Send to all available transmitters
    for endpoint in WS_ENDPOINTS:
        if current_availability[endpoint]:
            try:
                # Update transmitting status
                transmitting_status[endpoint] = True
                send_to_ws(endpoint, ric, msg, m_type, m_func)
                # Wait before sending to next transmitter
                time.sleep(T_DELAY)
                # Reset transmitting status after sending
                transmitting_status[endpoint] = False
            except Exception as e:
                print(f"Error sending to {endpoint}: {e}")
                # If sending fails, mark as not transmitting
                transmitting_status[endpoint] = False
    in_transmission = False

@app.route("/")
def index():
    return render_template('index.html', 
                         endpoints=WS_ENDPOINTS,
                         history=transmission_history,
                         ws_endpoints=WS_ENDPOINTS)

@app.route("/transmitting", methods=["GET"])
def transmitting():
    # Get current status
    current_status = {endpoint: transmitting_status[endpoint] for endpoint in WS_ENDPOINTS}
    current_availability = {endpoint: availability_status[endpoint] for endpoint in WS_ENDPOINTS}
    
    # Check if there's any change in status
    status_changed = False
    for endpoint in WS_ENDPOINTS:
        if current_status[endpoint] != previous_transmitting_status[endpoint]:
            status_changed = True
            break
    
    # Update previous status if there was a change
    if status_changed:
        previous_transmitting_status.update(current_status)
    
    return jsonify({
        "transmitting": any(transmitting_status.values()),
        "transmitters": current_status,
        "availability": current_availability
    })

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    ric = data.get("RIC")
    msg = data.get("MSG")
    m_type = data.get("m_type", "AlphaNum")
    m_func = data.get("m_func", "Func3")

    try:
        # Use the new dispatch function that skips offline transmitters
        dispatch_message(ric, msg, m_type, m_func)
        
        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transmission_history.insert(0, {
            "timestamp": timestamp,
            "ric": ric,
            "msg": msg,
            "m_type": m_type,
            "m_func": m_func
        })
        
        # Keep only the last MAX_HISTORY entries
        if len(transmission_history) > MAX_HISTORY:
            transmission_history.pop()
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
