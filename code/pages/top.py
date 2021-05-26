from flask import render_template, Blueprint, current_app
import numpy as np
import pandas as pd
import math
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

top_ = Blueprint('top', __name__, template_folder='templates')


@top_.route('/top')
def top():
    sp = current_app.config['sp']

    top_tracks_df = get_top_tracks_data(sp)
    top_tracks_df = pd.DataFrame(top_tracks_df)

    top_artist_df = create_top_artist_data(sp)
    top_genres_short = top_genres(top_artist_df)
    sunburst_data = create_sunburst_data(top_artist_df, top_genres_short)

    popular_df = get_top_songs_over_release_date_vs_popularity(sp)
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

    fig3 = go.Figure()
    fig3.add_trace(go.Sunburst(
        labels=sunburst_data['artist'],
        parents=sunburst_data['genres'],
    ))
    fig3.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    header = 'Data on your favorite artists'
    description = ''
    return render_template('top.html', graphJSON=graphJSON, graphJSON2=graphJSON2, graphJSON3=graphJSON3, header=header, description=description)


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

    results = sp.current_user_top_tracks(time_range="long_term", limit=50)
    for i, item in enumerate(results['items']):
        name = item['name']
        # if math.isnan(name):
        #     name = 'No Name'
        song_name.append(name)
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


def create_top_artist_data(sp):
    results = sp.current_user_top_artists(time_range='long_term', limit=100)
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
