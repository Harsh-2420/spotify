from flask import render_template, Blueprint, request, current_app
import time
from datetime import datetime
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json


user_collection_ = Blueprint(
    'user_collection', __name__, template_folder='templates')


@user_collection_.route('/user_collection')
def user_collection():
    mongo = current_app.config['mongo']
    collection = mongo.db.userTracks
    track = request.args.get('track')
    artist = request.args.get('artist')

    # Initial Run - with no input
    if track == None or artist == None:
        track_df = create_df(collection)
        graphJSON2 = plot_scatter(track_df)
        return render_template('user_collection.html', graphJSON=graphJSON2)
    # Secondary Run - with some input provided
    else:
        curr_time = int(time.time())
        # Check if data is new or existing and update collection
        update_db(collection, track, artist, curr_time)
        track_df = create_df(collection)
        graphJSON2 = plot_scatter(track_df)
        return render_template('user_collection.html', graphJSON=graphJSON2)


def plot_scatter(track_df):
    hover_text = []
    # bubble_size = []

    for index, row in track_df.iterrows():
        hover_text.append(('song name: {country}<br>' +
                           'count: {lifeExp}<br>' +
                           'release: {gdp}<br>' +
                           'artist: {year}').format(country=row['song_name'],
                                                    lifeExp=row['count'],
                                                    gdp=row['suggested_date'],
                                                    year=row['artist_name']))
        # bubble_size.append(math.sqrt(row['song_duration']))
    track_df['text'] = hover_text
    # track_df['size'] = bubble_size
    # sizeref = 2.*max(track_df['size'])/(100**2)
    d = dict(tuple(track_df.groupby('artist_name')))

    fig2 = go.Figure()
    for artist, data in d.items():
        fig2.add_trace(go.Scatter(
            x=data['suggested_date'], y=data['count'],
            name=artist, text=data['text'],
            # marker_size=data['size'],
        ))
        fig2.update_traces(mode='markers', marker=dict(sizemode='area',
                                                       #    sizeref=sizeref,
                                                       line_width=2))

    fig2.update_layout(
        title='Community Recommendations',
        xaxis=dict(
            title='Suggested Date',
            gridcolor='white',
            gridwidth=2,
        ),
        yaxis=dict(
            title='Count of Recommendations',
            gridcolor='white',
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON2


def update_db(collection, track, artist, curr_time):
    query = collection.find(
        {'track_check': track.lower(), 'artist_check': artist.lower()})

    count = query.count()
    if count == 0:
        collection.insert_one({'track': track, 'artist': artist, 'time': curr_time,
                              'track_check': track.lower(), 'artist_check': artist.lower(), 'count': count})
    else:
        for result in query:
            id = result['_id']
        collection.find_one_and_update({'_id': id}, {'$inc': {'count': 1}})


def create_df(collection):
    song_name = []
    artist_name = []
    suggested_date = []
    song_count = []
    for result in collection.find({}):
        song_name.append(result['track'])
        artist_name.append(result['artist'])
        time = datetime.utcfromtimestamp(result['time']).strftime('%Y-%m-%d')
        suggested_date.append(time)
        song_count = result['count']
        break
    df = pd.DataFrame({
        'song_name': song_name,
        'artist_name': artist_name,
        'suggested_date': suggested_date,
        'count': song_count

    })
    return df
