from flask import render_template, Blueprint, current_app
import numpy as np
import pandas as pd
import math
import plotly
import pickle
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

sunburst_ = Blueprint('sunburst', __name__, template_folder='templates')


@sunburst_.route('/sunburst/')
def sunburst():
    sp = current_app.config['sp']
    top_artist_df = create_top_artist_data(sp)
    top_genres_short = top_genres(top_artist_df)
    sunburst_data = create_sunburst_data(top_artist_df, top_genres_short)

    fig = go.Figure()
    fig.add_trace(go.Sunburst(
        labels=sunburst_data['artist'],
        parents=sunburst_data['genres'],
        # values=sunburst_data['values'],
    ))
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = ''
    description = ''
    return render_template('sunburst.html', graphJSON=graphJSON, header=header, description=description)


def create_top_artist_data(sp):
    results = sp.current_user_top_artists(time_range='long_term', limit=50)
    genre = []
    names = []
    for item in results['items']:
        if item['genres'] == []:
            continue
        else:
            genre.append(item['genres'])
            names.append(item['name'])
    df = pd.DataFrame()
    df['genres'] = genre
    df['name'] = names
    return df


def top_genres(df):
    genres_top_count = {}
    for genre_list in df['genres']:
        for genre in genre_list:
            if genre not in genres_top_count:
                genres_top_count[genre] = 1
            else:
                genres_top_count[genre] += 1
    genres_top_count = pd.Series(genres_top_count).sort_values(ascending=False)
    return genres_top_count.head()


def create_sunburst_data(df, top_genres):
    # pdb.set_trace()
    genres, artists, values = [], [], []
    for i, row in df.iterrows():
        for genre, value in top_genres.items():
            if genre in row['genres']:
                genres.append(genre)
                values.append(str(value))
                artists.append(row['name'])
                break

    unique_genre = set(genres)
    for g in unique_genre:
        genres.append('')
        artists.append(g)

    df = pd.DataFrame()
    df['artist'] = artists
    df['genres'] = genres

    return df
