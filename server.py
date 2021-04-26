import time
from flask import Flask, request, url_for, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

app.secret_key = "spotty"
app.config['SESSION_COOKIE_NAME'] = "Harsh Cookie"
TOKEN_INFO = "token_info"


@app.route('/')
def login():
    return "Logging in"


@app.route('/redirect')
def redirectPage():
    return "redirect"


@app.route('/getTracks')
def getTracks():
    return 'some drake songs'


if __name__ == "__main__":
    app.run(debug=True)
