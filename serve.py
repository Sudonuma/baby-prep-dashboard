"""Tiny local dev server for the static app: python serve.py → http://localhost:8123"""
import http.server
import os
import socketserver

os.chdir(os.path.dirname(os.path.abspath(__file__)))
socketserver.ThreadingTCPServer.allow_reuse_address = True

with socketserver.ThreadingTCPServer(("", 8123), http.server.SimpleHTTPRequestHandler) as httpd:
    print("Baby Prep (local-first) serving at http://localhost:8123 — Ctrl+C to stop")
    httpd.serve_forever()
