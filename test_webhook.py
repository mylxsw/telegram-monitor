#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Webhook Server
Receives and prints messages sent from Telegram Monitor

Usage:
    python test_webhook.py [port]

Default port: 8080
"""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle Webhook POST requests"""
    
    def do_POST(self):
        """Handle POST request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(body.decode('utf-8'))
            
            # Print received message
            print("\n" + "=" * 60)
            print(f"Received message @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            print(f"Group: {data.get('chat_name')} (ID: {data.get('chat_id')})")
            print(f"Sender: {data.get('sender_name')} (ID: {data.get('sender_id')})")
            print(f"Message ID: {data.get('message_id')}")
            print(f"Time: {data.get('date')}")
            print(f"Media: {'Yes' if data.get('media') else 'No'}")
            print(f"Content: {data.get('text', '(no text)')}")
            print("-" * 60)
            print(f"Complete JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("=" * 60 + "\n")
            
            # Return success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Disable default access logs"""
        pass


def main():
    """Start test Webhook server"""
    # Get port number
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid port number '{sys.argv[1]}'")
            sys.exit(1)
    
    # Create server
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    
    print("=" * 60)
    print("Test Webhook Server")
    print("=" * 60)
    print(f"Listening address: http://0.0.0.0:{port}")
    print(f"Local access: http://localhost:{port}")
    print(f"Webhook URL: http://localhost:{port}/webhook")
    print("-" * 60)
    print("Press Ctrl+C to stop server")
    print("=" * 60 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
