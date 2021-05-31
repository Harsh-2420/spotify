from flask import render_template, Blueprint, current_app, request, session
import numpy as np
import pandas as pd
import tweepy
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from os import environ
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import spotipy


twitter_top_ = Blueprint('twitter_top', __name__, template_folder='templates')

twitter_consumer_key = environ['twitter_consumer_key']
twitter_consumer_secret = environ['twitter_consumer_secret']
twitter_callback_uri = environ['twitter_callback_uri']
twitter_access_token = environ['twitter_access_token']
twitter_access_token_secret = environ['twitter_access_token_secret']


@twitter_top_.route('/twitter_top')
def twitter_top():
    # sp = current_app.config['sp']
    # sp = session.get('sp', None)
    token_info = session.get('token_info', None)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)
    top_artist_df = create_top_artist_data(sp, api)

    fig = px.scatter_3d(top_artist_df, x='positive', y='negative', z='neutral',
                        color='name')
    # fig.show()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('twitter.html', graphJSON=graphJSON)


def create_top_artist_data(sp, api):
    results = sp.current_user_top_artists(time_range='long_term', limit=100)
    names = []
    positive = []
    negative = []
    neutral = []
    for item in results['items']:
        name = item['name']
        try:
            sentiments = get_sentiment(api, name)
            positive.append(sentiments[0][1])
            negative.append(sentiments[1][1])
            neutral.append(sentiments[2][1])
            names.append(name)
        except:
            continue

    df = pd.DataFrame()
    df['name'] = names
    df['positive'] = positive
    df['negative'] = negative
    df['neutral'] = neutral
    return df


def clean(tweet):
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = re.sub(r'#', '', tweet)
    tweet = re.sub(r'@[A-Za-z0–9]+', '', tweet)
    return tweet


def get_sentiment(api, key):

    tweet_limit = 100
    keyword = key
    tweets = tweepy.Cursor(api.search, q=keyword,
                           result_type='popular').items(tweet_limit)
    tweet_list = []
    negative_list = []
    neutral_list = []
    positive_list = []
    positive = 0
    negative = 0
    neutral = 0
    for tweet in tweets:
        text = tweet.text
        text = clean(text)
        tweet_list.append(text)
        score = SentimentIntensityAnalyzer().polarity_scores(text)
        neg = score['neg']
        pos = score['pos']
        if neg > pos:
            negative_list.append(text)
            negative += 1
        elif pos > neg:
            positive_list.append(text)
            positive += 1

        elif pos == neg:
            neutral_list.append(text)
            neutral += 1
    positive = round(percentage(positive, len(tweet_list)))
    negative = round(percentage(negative, len(tweet_list)))
    neutral = round(percentage(neutral, len(tweet_list)))
    positive = format(positive, '.1f')
    negative = format(negative, '.1f')
    neutral = format(neutral, '.1f')
    results = [["positive", positive], [
        'negative', negative], ['neutral', neutral]]
    return results


def percentage(part, whole):
    return 100 * float(part)/float(whole)
