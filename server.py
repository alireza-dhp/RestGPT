from flask import Flask, request
import threading
import time
import os
import logging
from requests_oauthlib import OAuth2Session
import yaml



app = Flask(__name__)
authorization_code = None
server_thread = None
shutdown_flag = threading.Event()
logger = logging.getLogger()

@app.route('/callback')
def callback():
    global authorization_code
    authorization_code = request.args.get('code')
    shutdown_flag.set()
    return "Authorization successful! You can close this window now."

def run_server():
    app.run(port=5000, threaded=True)

def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

def stop_server():
    shutdown_flag.wait(timeout=60)  # Wait for up to 60 seconds
    if not shutdown_flag.is_set():
        print("Timeout waiting for authorization. Please try again.")
        return None
    time.sleep(1)  # Give a moment for the callback to complete
    return authorization_code

def get_access_token(scopes):
        config = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
        client_id = config["GOOGLE_CLIENT_ID"]
        client_secret = config["GOOGLE_CLIENT_SECRET"]
        authorization_base_url = config["AUTHORIZATION_URL"]
        token_url = config["TOKEN_URL"]
        redirect_uri = config["REDIRECT_URI"]
        #scope = config["GOOGLE_SCOPE").split()
        
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        authorization_url, _ = oauth.authorization_url(authorization_base_url, access_type="offline", prompt="consent")

        logger.info(f"Please go to this URL and authorize access: [Authorize]({authorization_url})")

        start_server()
        authorization_code = stop_server()

        if authorization_code is None:
            return None

        token = oauth.fetch_token(token_url, code=authorization_code, client_secret=client_secret)
        access_token = token['access_token']

        return access_token