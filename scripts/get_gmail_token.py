#!/usr/bin/env python3
"""
JobRadar — Gmail OAuth Token Setup Script
Run this once to authenticate and retrieve your refresh token.
Save the printed refresh token into your .env file.

Usage:
  pip install google-auth-oauthlib
  python scripts/get_gmail_token.py
"""

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import urllib.parse

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080"
SCOPES = "https://www.googleapis.com/auth/gmail.send"

auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>JobRadar: Authorization successful! You can safely close this browser window.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

    def log_message(self, format, *args):
        pass


def main():
    global CLIENT_ID, CLIENT_SECRET

    if not CLIENT_ID:
        CLIENT_ID = input("Enter your Google Client ID: ").strip()
    if not CLIENT_SECRET:
        CLIENT_SECRET = input("Enter your Google Client Secret: ").strip()

    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Google Client ID and Secret are required.")
        return

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={urllib.parse.quote(CLIENT_ID)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    print("\n=== JobRadar Gmail OAuth Setup ===")
    print("Opening your browser for authorization...")
    webbrowser.open(auth_url)
    print("Listening on http://localhost:8080 for callback...")

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()

    if not auth_code:
        print("ERROR: Did not receive authorization code.")
        return

    # Exchange code for token
    token_data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Token exchange error: {e}")
        return

    refresh_token = tokens.get("refresh_token")
    if refresh_token:
        print("\n" + "=" * 50)
        print(" SUCCESS! Copy this to your .env file:")
        print("=" * 50)
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print("=" * 50 + "\n")
    else:
        print("\nERROR: No refresh token received in response.")
        print("Response:", json.dumps(tokens, indent=2))


if __name__ == "__main__":
    main()
