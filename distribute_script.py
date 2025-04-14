import time
import threading
import json
import websocket
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
PASSWORD = "your_password"
WS_ENDPOINTS = ["ws://192.168.188.21:8055", "ws://192.168.188.22:8055"]  # Add more as needed
T_DELAY = 5.0  # Delay in seconds between sends

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

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    ric = data.get("RIC")
    msg = data.get("MSG")
    m_type = data.get("m_type")
    m_func = data.get("m_func")

    def dispatch():
        for endpoint in WS_ENDPOINTS:
            send_to_ws(endpoint, ric, msg, m_type, m_func)
            time.sleep(T_DELAY)

    threading.Thread(target=dispatch).start()
    return jsonify({"status": "Message dispatch initiated"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
