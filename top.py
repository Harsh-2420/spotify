from flask import render_template, Blueprint, current_app
import numpy as np
import pandas as pd
import math
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

top = Blueprint('top', __name__, template_folder='templates')


@top.route('/chart1')
def chart1():
    sp = current_app.config['sp']

    top_tracks_df = get_top_tracks_data(sp)
    top_tracks_df = pd.DataFrame(top_tracks_df)

    # genre_df = get_genres(sp)

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
        header=dict(values=['long_term', 'medium_term', 'short_term', 'date'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[top_tracks_df.long_term, top_tracks_df.medium_term, top_tracks_df.short_term, popular_df.release_date],
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
            # type='',
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

    # fig3 = px.sunburst(genre_df, path=['parent_genre', 'artist_name_list'])
    # fig3 = go.Figure()
    # fig3.add_trace(go.Table(
    #     header=dict(values=genre_df.columns,
    #                 fill_color='paleturquoise',
    #                 align='left'),
    #     cells=dict(values=[genre_df.parent_genre, genre_df.artist_name_list],
    #                fill_color='lavender',
    #                align='left')
    # ))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    # graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Get top tweets based on a keyword"
    description = """
    Use a given keyword to get most popular tweets. Give option for recent and custom keyword
    """
    return render_template('notdash2.html', graphJSON=graphJSON, graphJSON2=graphJSON2, header=header, description=description)


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
