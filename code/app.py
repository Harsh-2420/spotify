# Flask imports
from flask import Flask, request, url_for, redirect, session, render_template
from flask_session import Session

# Blueprint imports
# from pages.recommend import recommend_
from pages.top import top_
from pages.sunburst import sunburst_

# Spotipy imports
import time
from git_ignore.config import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
# app.register_blueprint(recommend_, url_prefix="")
app.register_blueprint(top_, url_prefix="")
app.register_blueprint(sunburst_, url_prefix="")

app.secret_key = "spotty"
sess = Session()
app.config['SESSION_COOKIE_NAME'] = "JJ Cookie"
TOKEN_INFO = "token_i"


@app.route('/')
def login():
    sp_oauth = create_spotify_ouath()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_ouath()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))


@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    app.config['sp'] = sp
    return render_template('index.html')


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_ouath()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_ouath():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-top-read user-library-read")


if __name__ == "__main__":
    app.run(debug=True)