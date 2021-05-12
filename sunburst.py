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


@sunburst_.route('/sunburst')
def sunburst():
    sp = current_app.config['sp']
    genre_df = get_genres(sp)
    fig = px.sunburst(genre_df, path=['parent_genre', 'artist_name_list'])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Get top tweets based on a keyword"
    description = """
    Use a given keyword to get most popular tweets. Give option for recent and custom keyword
    """
    return render_template('top.html', graphJSON=graphJSON, header=header, description=description)


def get_genres(sp):
    parent_genre = []
    artist_name_list = []
    results = sp.current_user_top_tracks(time_range='short_term', limit=50)
    for i, item in enumerate(results['items']):
        artist_name = item['artists'][0]['name']
        search = sp.search(artist_name)
        track = search['tracks']['items'][0]
        artist = sp.artist(track["artists"][0]["external_urls"]["spotify"])
        genre_list = artist['genres']
        top_genres = get_top_genres()
        for genre in top_genres:
            if len(genre_list) > 0:
                if genre in genre_list:
                    parent_genre.append(genre)
                    artist_name_list.append(artist_name)
    genre_df = pd.DataFrame()
    genre_df['parent_genre'] = parent_genre
    genre_df['artist_name_list'] = artist_name_list
    return genre_df


def get_top_genres():
    with open('./pickle/top_genres.pkl', 'rb') as handle:
        top_genres = pickle.load(handle)
    return top_genres
