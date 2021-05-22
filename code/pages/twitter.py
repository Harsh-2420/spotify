from flask import render_template, Blueprint, current_app, request
import numpy as np
import pandas as pd
import tweepy
import json
from datetime import datetime
from os import environ
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re


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
    key = request.args.get('key')
    num = request.args.get('num')
    if key == None:
        iteration = 0
        public_tweets = tweepy.Cursor(api.search, q='World',
                                      result_type='popular').items(int(10))
        return render_template('twitter.html', tweets=public_tweets, iteration=iteration)
    else:
        if not isinstance(key, str):
            try:
                public_tweets = tweepy.Cursor(api.search, q='World',
                                              result_type='popular').items(int(10))
            except:
                public_tweets = tweepy.Cursor(api.search, q='World',
                                              result_type='popular').items(int(10))
            return render_template('twitter.html', tweets=public_tweets, iteration=0)
        iteration = 1
        try:
            public_tweets = tweepy.Cursor(api.search, q=key,
                                          result_type='popular').items(int(num))
        except:
            public_tweets = tweepy.Cursor(api.search, q=key,
                                          result_type='popular').items(int(10))
        sentiments = get_sentiment(api, key)
        return render_template('twitter.html', tweets=public_tweets, iteration=iteration, key=key, sentiments=sentiments)


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
    if tweet_list:
        positive = round(percentage(positive, len(tweet_list)))
        negative = round(percentage(negative, len(tweet_list)))
        neutral = round(percentage(neutral, len(tweet_list)))
        positive = format(positive, '.1f')
        negative = format(negative, '.1f')
        neutral = format(neutral, '.1f')
        results = [["positive", positive], [
            'negative', negative], ['neutral', neutral]]
        return results
    else:
        return 'error'


def percentage(part, whole):
    return 100 * float(part)/float(whole)
