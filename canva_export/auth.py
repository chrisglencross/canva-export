import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

import pkce
import requests
import yaml
from requests.auth import HTTPBasicAuth


class Session:
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

def get_session(client_id, client_secret, redirect_port=3001):

    session = read_cached_session()
    if session:
        try:
            if refresh_session(client_id, client_secret, session):
                return session
        except Exception as e:
            print("Error loading previous Canva Session: \n" + str(e) )

    code_verifier = pkce.generate_code_verifier(length=128)
    code_challenge = pkce.get_code_challenge(code_verifier)
    authorization_code = None

    class AuthorizationHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal authorization_code
            if self.path.startswith("/oauth/redirect?"):
                authorization_code = self.path.split("?code=")[1]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authorization Code Received</h1>")
            else:
                self.send_response_only(404)

    with HTTPServer(('', redirect_port), AuthorizationHandler) as httpd:
        webbrowser.open(f"https://www.canva.com/api/oauth/authorize?code_challenge_method=s256&response_type=code&client_id={client_id}&scope=design:content:read%20design:meta:read&code_challenge={code_challenge}")
        httpd.handle_request()

    response = requests.post(
        "https://api.canva.com/rest/v1/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=HTTPBasicAuth(client_id, client_secret),
        data={
            'grant_type': "authorization_code",
            'code_verifier': code_verifier,
            'code': authorization_code
        })
    response.raise_for_status()
    payload = response.json()
    session = Session(payload['access_token'], payload['refresh_token'])
    write_cached_session(session)
    return session


def refresh_session(client_id, client_secret, session: Session):
    response = requests.post(
        "https://api.canva.com/rest/v1/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=HTTPBasicAuth(client_id, client_secret),
        data={
            'grant_type': "refresh_token",
            'refresh_token': session.refresh_token
        })
    response.raise_for_status()
    payload = response.json()
    session.access_token = payload['access_token']
    session.refresh_token = payload['refresh_token']
    write_cached_session(session)
    return True


def read_cached_session() -> Optional[Session]:
    try:
        with open('.session.yaml', 'r') as session_file:
            previous_session = yaml.safe_load(session_file)
            return Session(access_token=previous_session['access_token'], refresh_token=previous_session['refresh_token'])
    except OSError:
        return None

def write_cached_session(session: Session):
    with open('.session.yaml', 'w') as f:
        yaml.dump( {
            'access_token': session.access_token,
            'refresh_token': session.refresh_token
        }, f)
