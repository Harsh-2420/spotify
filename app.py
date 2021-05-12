import time
from flask import Flask, request, url_for, redirect, session, render_template
import plotly
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

    return render_template('index.html')


@app.route('/chart1')
def chart1():
    top_tracks_df = session.get('top_tracks', None)
    top_tracks_df = pd.DataFrame(top_tracks_df)

    popular_df = session.get('popular_df', None)
    popular_df = pd.DataFrame(popular_df)
    hover_text = []
    bubble_size = []

    for index, row in popular_df.iterrows():
        hover_text.append(('song name: {country}<br>' +
                           'popularity: {lifeExp}<br>' +
                           'release: {gdp}<br>' +
                           'duration: {pop}<br>' +
                           'artist: {year}').format(country=row['song_name'],
                                                    lifeExp=row['song_popularity'],
                                                    gdp=row['release_date'],
                                                    pop=row['song_duration'],
                                                    year=row['artist_name']))
        bubble_size.append(math.sqrt(row['song_duration']))
    popular_df['text'] = hover_text
    popular_df['size'] = bubble_size
    sizeref = 2.*max(popular_df['size'])/(100**2)

    d = dict(tuple(popular_df.groupby('artist_name')))

    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=['long_term', 'medium_term', 'short_term'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[top_tracks_df.long_term, top_tracks_df.medium_term, top_tracks_df.short_term],
                   fill_color='lavender',
                   align='left'))
                  )
    fig2 = go.Figure()
    for artist, data in d.items():
        fig2.add_trace(go.Scatter(
            x=data['release_date'], y=data['song_popularity'],
            name=artist, text=data['text'],
            marker_size=data['size'],
        ))
    fig2.update_traces(mode='markers', marker=dict(sizemode='area',
                                                   sizeref=sizeref, line_width=2))

    fig2.update_layout(
        title='Song Popularity vs Release Date',
        xaxis=dict(
            title='Release Date',
            gridcolor='white',
            type='log',
            gridwidth=2,
        ),
        yaxis=dict(
            title='Song Popularity',
            gridcolor='white',
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Get top tweets based on a keyword"
    description = """
    Use a given keyword to get most popular tweets. Give option for recent and custom keyword
    """
    return render_template('notdash2.html', graphJSON=graphJSON, graphJSON2=graphJSON2, header=header, description=description)


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


def get_top_songs_over_release_date_vs_popularity(sp):

    song_name = []
    release_date = []
    song_popularity = []
    song_duration = []
    artist_name = []

    results = sp.current_user_top_tracks(time_range="short_term", limit=20)
    for i, item in enumerate(results['items']):
        song_name.append(item['name'])
        date = sp.album(item["album"]["external_urls"]["spotify"])[
            'release_date']
        release_date.append(datetime.strptime(date, "%Y-%m-%d").date().year)
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
