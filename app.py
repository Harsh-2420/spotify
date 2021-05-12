import time
from flask import Flask, request, url_for, redirect, session, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from git_ignore.config import *
from datetime import datetime

app = Flask(__name__)

app.secret_key = "spotty"
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
    return str(top_tracks_df)

    # results = sp.current_user_top_tracks(time_range='short_term', limit=50)
    # temp = results['items'][1]["album"]

    # date = sp.album(temp["external_urls"]["spotify"])['release_date']
    # return str(datetime.strptime(date, "%Y-%m-%d").date().year)


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


if __name__ == "__main__":
    app.run(debug=True)



# def get_top_songs_over_release_date_vs_popularity(sp):

#     song_name = []
#     release_date = []
#     song_popularity = []
#     song_duration = []
#     artist_name = []

#     # tracks['short_term'] = []
#     results = sp.current_user_top_tracks(time_range="short_term", limit=20)
#     for i, item in enumerate(results['items']):
#         song_name.append(item['name'])
#         date = sp.album(item["album"]["external_urls"]["spotify"])[
#             'release_date']
#         release_date.append(datetime.strptime(date, "%Y-%m-%d").date().year)
#         song_popularity.append(item['popularity'])
#         song_duration.append(item['duration_ms'])
#         artist_name.append(item['artists'][0]['name'])

#     # df = pd.DataFrame(
#     # {'song_name': song_name,
#     #  'song_duration': song_duration,
#     #  'song_popularity': song_popularity,
#     #  'release_date': release_date,
#     #  'artist_name': artist_name
#     # })

#     return song_name, song_duration, song_popularity, release_date, artist_name
