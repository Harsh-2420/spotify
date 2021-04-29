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


server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/app/')

server.secret_key = "spotty"
server.config['SESSION_COOKIE_NAME'] = "Harsh Cookie"
TOKEN_INFO = "token_info"


@server.route('/')
def login():
    sp_oauth = create_spotify_ouath()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@server.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_ouath()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))


@server.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    df = get_saved_tracks_data(sp)
    with open('saved_tracks.pkl', 'wb') as f:
        pickle.dump(df, f)
    return {"Data": True}


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


def get_saved_tracks_data(sp):
    results = sp.current_user_saved_tracks(limit=20, offset=0)['items']
    date = []
    name = []
    for k, item in enumerate(results):
        date.append(datetime.strptime(
            item['added_at'][:11], '%Y-%m-%d').date())
        name.append(item['name'])
    df = pd.DataFrame(
        {'release_date': date,
         'name': name
         })
    return df


with open('saved_tracks.pkl', 'rb') as f:
    df = pickle.load(f)


app.layout = html.Div([
    dcc.Graph(id="scatter-plot"),
    html.P("Petal Width:"),
    dcc.RangeSlider(
        id='range-slider',
        min=0, max=2.5, step=0.1,
        marks={0: '0', 2.5: '2.5'},
        value=[0.5, 2]
    ),
])


@app.callback(
    Output("scatter-plot", "figure"),
    [Input("range-slider", "value")])
def update_bar_chart(slider_range):
    low, high = slider_range
    # mask = (df['petal_width'] > low) & (df['petal_width'] < high)
    fig = px.scatter(
        df, x="release_date", y="name",
        color="name")
    return fig


if __name__ == "__main__":
    app.run(debug=True)
