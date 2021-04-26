import time
from flask import Flask, request, url_for, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from git_ignore.config import *

app = Flask(__name__)

app.secret_key = "spotty"
app.config['SESSION_COOKIE_NAME'] = "Harsh Cookie"
TOKEN_INFO = "token_info"


@app.route('/')
def login():
    sp_oauth = create_spotify_ouath()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    return "redirect"


@app.route('/getTracks')
def getTracks():
    return 'some drake songs'


def create_spotify_ouath():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        # Where to come back to
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read")


if __name__ == "__main__":
    app.run(debug=True)
