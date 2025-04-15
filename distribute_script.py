import time
import threading
import json
import websocket
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# Configuration
PASSWORD = "your_password"
WS_ENDPOINTS = ["ws://192.168.188.21:8055", "ws://192.168.188.22:8055"]  # Add more as needed
T_DELAY = 5.0  # Delay in seconds between sends

# Global variable to store transmission history
transmission_history = []
MAX_HISTORY = 20

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

@app.route("/")
def index():
    return render_template('index.html', 
                         endpoints=WS_ENDPOINTS,
                         history=transmission_history)

@app.route("/transmitting", methods=["GET"])
def transmitting():
    # This endpoint will be used to check transmission status
    return jsonify({"transmitting": True})

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    ric = data.get("RIC")
    msg = data.get("MSG")
    m_type = data.get("m_type", "AlphaNum")
    m_func = data.get("m_func", "Func3")

    # print output in console
    print(f"Sending message to { ric } with message { msg } and type { m_type } and function { m_func }")

    # Add to transmission history
    transmission = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "ric": ric,
        "msg": msg,
        "m_type": m_type,
        "m_func": m_func
    }
    transmission_history.append(transmission)
    if len(transmission_history) > MAX_HISTORY:
        transmission_history.pop(0)

    def dispatch():
        for endpoint in WS_ENDPOINTS:
            send_to_ws(endpoint, ric, msg, m_type, m_func)
            time.sleep(T_DELAY)

    threading.Thread(target=dispatch).start()
    return jsonify({"status": "Message dispatch initiated"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
