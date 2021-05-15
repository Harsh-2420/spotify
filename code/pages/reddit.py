from flask import render_template, Blueprint, current_app
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
    reddit_obj = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret,
                             username=reddit_username, user_agent=reddit_user_agent)
    df = get_reddit_top_artist_data(sp, reddit_obj)

    fig = px.scatter(
        df.query('platform==1'),
        x="date", y="score",
        size="total comments",
        color="artist",
        hover_name="title")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('reddit.html', graphJSON=graphJSON)


def get_reddit_top_artist_data(sp, reddit_obj):
    results = sp.current_user_top_artists(time_range='long_term', limit=8)
    names = []
    for item in results['items']:
        names.append(item['name'])
    d = {}
    for x in names:
        d["{0}".format(x)] = reddit_obj.subreddit(x)
    df = pd.DataFrame()
    id_list = []
    title = []
    author = []
    comments = []
    date = []
    score = []
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
                score.append(sub.score)
                platform.append(1)
                artist.append(key)
        except:
            continue

    df['post_id'] = id_list
    df['title'] = title
    df['author'] = author
    df['total comments'] = comments
    df['date'] = date
    df['score'] = score
    df['platform'] = platform
    df['artist'] = artist
    return df
