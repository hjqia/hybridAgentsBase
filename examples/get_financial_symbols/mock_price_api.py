from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import random

class PriceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/price":
            params = urllib.parse.parse_qs(parsed.query)
            symbol = params.get("symbol", ["UNKNOWN"])[0]
            
            # Mock data
            price = round(random.uniform(10, 1000), 2)
            if symbol == "BTC": price = round(random.uniform(30000, 60000), 2)
            
            data = {
                "symbol": symbol,
                "price": price,
                "currency": "USD",
                "name": f"{symbol} Inc." if symbol != "BTC" else "Bitcoin"
            }
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PriceHandler)
    print(f"Price API running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
