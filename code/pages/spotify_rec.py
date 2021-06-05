from flask import render_template, Blueprint, current_app, session, request
import numpy as np
import pandas as pd
import math

from pandas.core.indexes import base
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import spotipy

spotify_rec_ = Blueprint('spotify_rec', __name__, template_folder='templates')


@spotify_rec_.route('/spotify_rec')
def spotify_rec():
    current_user_id = request.cookies.get('Spotty Cookie')
    all_sp_objects = current_app.config['all_sp_objects']
    token_info = all_sp_objects[current_user_id]
    sp = spotipy.Spotify(auth=token_info['access_token'])

    df = create_related_artist_df(sp)

    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=['Name', 'Popularity', 'Total Followers', 'Recommendation Based On', 'Genres'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.name, df.popularity, df.followers, df.based_on, df.genres],
                   fill_color='lavender',
                   align='left'))
                  )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = ""
    description = ''
    return render_template('spotify_rec.html', graphJSON=graphJSON, header=header, description=description)


def create_related_artist_df(sp):
    results = sp.current_user_top_artists(time_range='long_term', limit=10)
    name = []
    popularity = []
    genres = []
    followers = []
    based_on = []
    for item in results['items']:

        top_id = item['id']
        recs = sp.artist_related_artists(top_id)

        for rec in recs['artists']:
            based_on.append(item['name'])
            name.append(rec['name'])
            popularity.append(rec['popularity'])
            genres.append(rec['genres'])
            followers.append(rec['followers']['total'])
    df = pd.DataFrame()
    df['name'] = name
    df['popularity'] = popularity
    df['genres'] = genres
    df['followers'] = followers
    df['based_on'] = based_on
    # df.loc[df.astype(str).drop_duplicates(subset='genres', keep='first').index]
    return df
