from flask import render_template, Blueprint, current_app, request
import numpy as np
import pandas as pd
import math
import plotly
import praw
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from os import environ

reddit_ = Blueprint('reddit', __name__, template_folder='templates')

reddit_client_secret = environ['reddit_client_secret']
reddit_client_id = environ['reddit_client_id']
reddit_username = environ['reddit_username']
reddit_user_agent = environ['reddit_user_agent']


@reddit_.route('/reddit')
def reddit():
    sp = current_app.config['sp']
    key = request.args.get('key')
    reddit_obj = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret,
                             username=reddit_username, user_agent=reddit_user_agent)
    names = get_reddit_names(sp)
    df = get_reddit_top_artist_data(names, reddit_obj)

    fig = px.scatter(
        df.query('platform==1'),
        x="Date Created", y="Number of Upvotes",
        size="Total Comments on post",
        color="Artist Name",
        hover_name="Title")
    # hover_text = []
    # bubble_size = []
    # for index, row in df.iterrows():
    #     hover_text.append(('song name: {country}<br>' +
    #                        'popularity: {lifeExp}<br>' +
    #                        'release: {gdp}<br>' +
    #                        'duration: {pop}<br>').format(country=row['Artist Name'],
    #                                                      lifeExp=row['Date Created'],
    #                                                      gdp=row['Number of Upvotes'],
    #                                                      pop=row['Total Comments on post']))
    #     bubble_size.append(row['Total Comments on post'])
    # df['text'] = hover_text
    # df['size'] = bubble_size
    # d = dict(tuple(df.groupby('Artist Name')))
    # fig = go.Figure()
    # for artist, data in d.items():
    #     fig.add_trace(go.Scatter(
    #         x=data['Date Created'], y=data['Number of Upvotes'],
    #         name=artist, text=data['text'],
    #         marker_size=data['size'],
    #     ))

    if key == None:
        iteration = 0
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('reddit.html', graphJSON=graphJSON, iteration=iteration)
    else:
        iteration = 1
        new_df = get_new_df(key, reddit_obj)
        if isinstance(new_df, str):
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('reddit.html', graphJSON=graphJSON, iteration=0)

        hover_text_new = []
        bubble_size_new = []
        for index, row in new_df.iterrows():
            hover_text_new.append(('song name: {country}<br>' +
                                   'popularity: {lifeExp}<br>' +
                                   'release: {gdp}<br>' +
                                   'duration: {pop}<br>').format(country=row['Artist Name'],
                                                                 lifeExp=row['Date Created'],
                                                                 gdp=row['Number of Upvotes'],
                                                                 pop=row['Total Comments on post']))
        bubble_size_new.append(row['Total Comments on post'])
        new_df['text'] = hover_text_new
        new_df['size'] = bubble_size_new
        new_d = dict(tuple(new_df.groupby('Artist Name')))
        for artist, data in new_d.items():
            fig.add_trace(go.Scatter(
                x=data['Date Created'], y=data['Number of Upvotes'],
                name=artist, text=data['text'],
                marker_size=data['size'],
            ))

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('reddit.html', graphJSON=graphJSON, iteration=iteration)


def get_reddit_names(sp):
    results = sp.current_user_top_artists(time_range='long_term', limit=8)
    names = []
    for item in results['items']:
        names.append(item['name'])
    return names


def get_reddit_top_artist_data(names, reddit_obj):
    d = {}
    for x in names:
        d["{0}".format(x)] = reddit_obj.subreddit(x)
    df = pd.DataFrame()
    id_list = []
    title = []
    author = []
    comments = []
    date = []
    upvotes = []
    platform = []
    artist = []
    for key, val in d.items():
        try:
            for sub in val.hot(limit=50):
                time = datetime.utcfromtimestamp(
                    sub.created).strftime('%Y-%m-%d')
                id_list.append(sub.id)
                title.append(sub.title)
                author.append(sub.author)
                comments.append(sub.num_comments)
                date.append(time)
                upvotes.append(sub.score)
                platform.append(1)
                artist.append(key)
        except:
            continue

    df['post_id'] = id_list
    df['Title'] = title
    df['Author'] = author
    df['Total Comments on post'] = comments
    df['Date Created'] = date
    df['Number of Upvotes'] = upvotes
    df['platform'] = platform
    df['Artist Name'] = artist
    return df


def get_new_df(key, reddit_obj):
    d = {}
    try:
        d[key] = reddit_obj.subreddit(key)
    except:
        return 'No Subreddit Found'
    df = pd.DataFrame()
    id_list = []
    title = []
    author = []
    comments = []
    date = []
    upvotes = []
    platform = []
    artist = []
    for key, val in d.items():
        try:
            for sub in val.hot(limit=50):
                time = datetime.utcfromtimestamp(
                    sub.created).strftime('%Y-%m-%d')
                id_list.append(sub.id)
                title.append(sub.title)
                author.append(sub.author)
                comments.append(sub.num_comments)
                date.append(time)
                upvotes.append(sub.score)
                platform.append(1)
                artist.append(key)
        except:
            continue

    df['post_id'] = id_list
    df['Title'] = title
    df['Author'] = author
    df['Total Comments on post'] = comments
    df['Date Created'] = date
    df['Number of Upvotes'] = upvotes
    df['platform'] = platform
    df['Artist Name'] = artist
    return df
