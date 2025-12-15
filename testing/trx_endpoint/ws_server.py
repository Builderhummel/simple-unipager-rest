# fake_ws_server.py
import json
from datetime import datetime
from websocket_server import WebsocketServer

def on_message(client, server, message):
    print(f"\n[WS] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Message received")
    print(f"[WS] From client: {client['address']}")
    print(f"[WS] Raw payload: {message}")

    try:
        parsed = json.loads(message)
        print(f"[WS] Parsed JSON:\n{json.dumps(parsed, indent=2)}")
    except Exception as e:
        print(f"[WS] JSON parse error: {e}")

if __name__ == "__main__":
    ws = WebsocketServer(host="0.0.0.0", port=8055)
    ws.set_fn_message_received(on_message)
    print("[WS] WebSocket server running on ws://0.0.0.0:8055")
    ws.run_forever()
