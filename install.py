import http.server
import socketserver
import urllib.parse
import requests
import os
import sys
import dotenv


# --- CONFIGURATION ---
# Use the 'Client ID' and 'Client Secret' from Settings -> Credentials
dotenv.load_dotenv(override=True)
CLIENT_ID = os.environ["APP_CLIENT_ID"]
API_SECRET = os.environ["APP_SECRET"]

# Add the permissions your script needs (comma-separated)
SCOPES = "read_products,write_products,read_inventory,write_inventory,read_files,write_files,read_metaobjects,write_metaobjects,read_metaobject_definitions,write_metaobject_definitions"

PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}"


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        shop = query.get("shop", [None])[0]
        code = query.get("code", [None])[0]

        # STEP 1: Initial redirect from Dashboard (No code yet, but has shop)
        if shop and not code:
            auth_url = (
                f"https://{shop}/admin/oauth/authorize?"
                f"client_id={CLIENT_ID}&"
                f"scope={SCOPES}&"
                f"redirect_uri={REDIRECT_URI}"
            )
            print(f"[*] Redirecting to Shopify for approval: {shop}")
            self.send_response(302)
            self.send_header("Location", auth_url)
            self.end_headers()

        # STEP 2: Return from Shopify (We have the code!)
        elif code:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h1>Success!</h1><p>Check your terminal for the token.</p>"
            )

            print(f"[!] Captured Code: {code}")
            self.exchange_for_token(shop, code)
            print("\n[+] Task complete. Closing server...")
            sys.exit(0)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Missing shop or code parameters.")

    def exchange_for_token(self, shop, code):
        print(f"[*] Exchanging code for permanent access token for {shop}...")
        url = f"https://{shop}/admin/oauth/access_token"
        payload = {"client_id": CLIENT_ID, "client_secret": API_SECRET, "code": code}
        res = requests.post(url, json=payload).json()
        if "access_token" in res:
            print("\n" + "=" * 60)
            print("YOUR PERMANENT ACCESS TOKEN (shpat_...):")
            print(f" {res['access_token']}")
            print("=" * 60)
        else:
            print(f"\n[!] Exchange failed: {res}")


if __name__ == "__main__":
    print(f"[*] Server listening on {REDIRECT_URI}...")
    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        httpd.serve_forever()
