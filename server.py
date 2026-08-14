#!/usr/bin/env python3
"""
Simple HTTP Server with API endpoint for Teacher Lewis's Practice Book Studio
Supports serving static files and saving annotations directly to disk.
"""

import http.server
import socketserver
import json
import os

PORT = 8000
ANNOTATIONS_FILE = os.path.join('output_json', 'workbook_custom_annotations.json')

class StudioRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/api/save_annotations':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                os.makedirs('output_json', exist_ok=True)
                with open(ANNOTATIONS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": f"Saved annotations to {ANNOTATIONS_FILE}"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def end_headers(self):
        # Enable CORS for convenience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    print(f"[+] Launching Teacher Lewis's Practice Book Server on http://localhost:{PORT}")
    print(f"[+] Studio Ghibli Landing Hub: http://localhost:{PORT}/index.html")
    print(f"[+] Full Interactive Reader: http://localhost:{PORT}/workbook.html")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), StudioRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

