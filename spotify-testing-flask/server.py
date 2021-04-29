import time
from flask import Flask, request, url_for, redirect, session, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import *
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import json
from datetime import datetime


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

    # top_tracks_df = get_top_tracks_data(sp)
    # top_artists_df = get_top_artists_data(sp)
    results = sp.current_user_saved_tracks(limit=20, offset=0)
    # return render_template('base.html',
    #                        tables=[top_artists_df.to_html(
    #                            classes='data'), top_tracks_df.to_html(classes='data')],
    #                        titles=[top_artists_df.columns.values, top_tracks_df.columns.values])
    return results


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
        scope="user-library-read")


def get_top_tracks_data(sp):
    ranges = ['short_term', 'medium_term', 'long_term']
    tracks = {}
    for sp_range in ranges:
        tracks[sp_range] = []
        results = sp.current_user_top_tracks(time_range=sp_range, limit=20)
        for i, item in enumerate(results['items']):
            val = item['name']
            tracks[sp_range].append(val)
    top_tracks_df = pd.DataFrame(tracks)
    return top_tracks_df


def get_top_artists_data(sp):
    ranges = ['short_term', 'medium_term', 'long_term']
    artists = {}
    for sp_range in ranges:
        artists[sp_range] = []
        results = sp.current_user_top_artists(time_range=sp_range, limit=15)
        for i, item in enumerate(results['items']):
            val = item['name']
            artists[sp_range].append(val)
    top_artists_df = pd.DataFrame(artists)
    return top_artists_df


if __name__ == "__main__":
    app.run(debug=True)
