# fake_status_server.py
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[HTTP] GET {self.path} from {self.client_address}")

        if self.path == "/status.json":
            payload = {
                "status": "ok",
                "mock": True,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            body = json.dumps(payload).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print("[HTTP] → 200 status.json")
        else:
            self.send_response(404)
            self.end_headers()
            print("[HTTP] → 404")

    def log_message(self, format, *args):
        return  # Suppress extra logging

if __name__ == "__main__":
    httpd = HTTPServer(("0.0.0.0", 8073), StatusHandler)
    print("[HTTP] Status server running on http://0.0.0.0:8073/status.json")
    httpd.serve_forever()
