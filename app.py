import time
from flask import Flask, request, url_for, redirect, session, render_template
from recommend import recommend
from top import top
from flask.globals import g
import plotly
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
import tweepy
from flask_session import Session
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from git_ignore.config import *
from datetime import datetime
from flask_session import Session
import json
import pandas as pd
import math

app = Flask(__name__)
app.register_blueprint(recommend, url_prefix="")
app.register_blueprint(top, url_prefix="")

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

    top_tracks_df = get_top_tracks_data(sp)
    session['top_tracks'] = top_tracks_df

    popular_df = get_top_songs_over_release_date_vs_popularity(sp)
    popular_df = popular_df.to_dict()
    session['popular_df'] = popular_df

    # genre_df = get_genres(sp)
    # genre_df = genre_df.to_dict()
    # session['genre_df'] = genre_df

    return render_template('index.html')


@app.route("/predict", methods=['POST'])
def upload():
    if request.method == "POST":
        num = int(request.form['rec'])
        names = request.form['text'].split(',')
        weights = request.form['weight'].split(',')
        artists = {}
        for k, name in enumerate(names):
            artists[name.strip()] = int(weights[k])
        preds = get_similar_artists_multiple(artists, num)
        return str(preds)
    return 'upload func ran'


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




def get_top_tracks_data(sp):
    ranges = ['short_term', 'medium_term', 'long_term']
    tracks = {}
    for sp_range in ranges:
        tracks[sp_range] = []
        results = sp.current_user_top_tracks(
            time_range=sp_range, limit=30, offset=0)
        for i, item in enumerate(results['items']):
            val = item['artists'][0]['name']
            tracks[sp_range].append(val)
    return tracks


def get_top_songs_over_release_date_vs_popularity(sp):

    song_name = []
    release_date = []
    song_popularity = []
    song_duration = []
    artist_name = []

    results = sp.current_user_top_tracks(time_range="long_term", limit=30)
    for i, item in enumerate(results['items']):
        song_name.append(item['name'])
        date = sp.album(item["album"]["external_urls"]["spotify"])[
            'release_date']
        try:
            date = str(datetime.strptime(date, "%Y-%m-%d").date())
            date = date[:len(date) - 13]
        except:
            date = str(datetime.strptime(date, "%Y").date())
            date = date[:len(date) - 13]
        release_date.append(date)
        song_popularity.append(item['popularity'])
        song_duration.append(item['duration_ms'])
        artist_name.append(item['artists'][0]['name'])

    df = pd.DataFrame(
        {'song_name': song_name,
         'song_duration': song_duration,
         'song_popularity': song_popularity,
         'release_date': release_date,
         'artist_name': artist_name
         })

    return df



# def get_genres(sp):
#     parent_genre = []
#     artist_name_list = []
#     results = sp.current_user_top_tracks(time_range='short_term', limit=50)
#     for i, item in enumerate(results['items']):
#         artist_name = item['artists'][0]['name']
#         search = sp.search(artist_name)
#         track = search['tracks']['items'][0]
#         artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
#         genre_list = artist['genres']
#         top_genres = get_top_genres()
#         for genre in top_genres:
#             if len(genre_list) > 0:
#                 if genre in genre_list:
#                     parent_genre.append(genre)
#                     artist_name_list.append(artist_name)
#     genre_df = pd.DataFrame()
#     genre_df['parent_genre'] = parent_genre
#     genre_df['artist_name_list'] = artist_name_list
#     return genre_df


# def get_top_genres():
#     with open('./pickle/top_genres.pkl', 'rb') as handle:
#         top_genres = pickle.load(handle)
#     return top_genres
if __name__ == "__main__":
    app.run(debug=True)
