import time
from flask import Flask, request, url_for, redirect, session, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from git_ignore.config import *
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff

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
    # return sp.current_user_top_artists(time_range='medium_term', limit=20, offset=0)
    # return sp.current_user_saved_tracks(limit=20, offset=0)

    top_tracks_df = get_top_tracks_data(sp)
    top_artists_df = get_top_artists_data(sp)
    return render_template('base.html',
                           tables=[top_artists_df.to_html(
                               classes='data'), top_tracks_df.to_html(classes='data')],
                           titles=[top_artists_df.columns.values, top_tracks_df.columns.values])


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


def get_top_albums(sp):
    ranges = ['short_term', 'medium_term', 'long_term']
    albums = {}
    for sp_range in ranges:
        albums[sp_range] = []
        results = sp.current_user_top_tracks(time_range=sp_range, limit=20)
        for i, item in enumerate(results['items']):
            val = item['album']['name']
            albums[sp_range].append(val)
    top_albums_df = pd.DataFrame(tracks)
    return top_albums_df


def plot_top_songs_over_release_date_vs_popularity(sp):
    tracks = {}
    tracks['short_term'] = []
    results = sp.current_user_top_tracks(time_range="short_term", limit=20)
    for i, item in enumerate(results['items']):
        song_name = val['name']
        release_date = sp.album(item["album"]["external_urls"]["spotify"])[
            'release_date']
        release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        song_popularity = item['popularity']  # int
        song_duration = item['duration_ms']

        tracks[sp_range].append(val)

    df = px.data.gapminder()
    fig = px.scatter(df.query("year==2007"), x="gdpPercap", y="lifeExp",
                     size="pop", color="continent",
                     hover_name="country", log_x=True, size_max=60)
    fig.show()
# def plot_top_albums(df):
#     return dcc.Graph(
#         id='top-albums',
#         figure={
#             'data': [
#                 go.Table(
#                     columnwidth=[35, 20, 11],
#                     header=dict(
#                         values=list(
#                             f"<b>{c}</b>" for c in
#                             df.columns),
#                         fill_color='#1759c2',
#                         align='center',
#                         height=30,
#                         font=dict(color='white', size=18)
#                     ),
#                     cells=dict(values=[df[c] for c in
#                                        df.columns],
#                                # fill_color=['white', 'white', clrs_6_mo, clrs_last_mo],
#                                line_color='#e1f0e5',
#                                align='center',
#                                font=dict(color='black', size=18),
#                                height=30
#                                )
#                 )
#             ],
#             'layout': go.Layout(
#                 margin=dict(t=0, l=0, r=0, b=0),
#                 height=800
#             )
#         }
#     )


if __name__ == "__main__":
    app.run(debug=True)
