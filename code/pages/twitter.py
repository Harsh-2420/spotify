from flask import render_template, Blueprint, current_app, request
import numpy as np
import pandas as pd
import tweepy
import json
from datetime import datetime
from os import environ

twitter_ = Blueprint('twitter', __name__, template_folder='templates')

twitter_consumer_key = environ['twitter_consumer_key']
twitter_consumer_secret = environ['twitter_consumer_secret']
twitter_callback_uri = environ['twitter_callback_uri']
twitter_access_token = environ['twitter_access_token']
twitter_access_token_secret = environ['twitter_access_token_secret']


@twitter_.route('/twitter')
def twitter():
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)
    search = request.args.get('q')
    public_tweets = api.user_timeline(search)
    # tweets = tweepy.Cursor(api.search, q='Drake',
    #                        result_type='popular').items(10)
    return render_template('twitter.html', tweets=public_tweets)
