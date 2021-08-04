# Flask imports
from flask import Flask, request, url_for, redirect, session, render_template
from flask_session import Session
from flask_pymongo import PyMongo
import sys
import uuid
import pandas as pd
import numpy as np
import math
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

import pandas as pd
from pymongo import MongoClient
import json
import requests

import urllib


# twitter imports
import tweepy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

# Reddit Imports
import praw

# Spotipy imports
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from os import environ

mongo_uri = environ.get('MONGO_URI')
app = Flask(__name__)

app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

# SPOTIPY_CLIENT_ID = environ['SPOTIPY_CLIENT_ID']
# SPOTIPY_CLIENT_SECRET = environ['SPOTIPY_CLIENT_SECRET']

# Twitter Keys
twitter_consumer_key = environ['twitter_consumer_key']
twitter_consumer_secret = environ['twitter_consumer_secret']
twitter_callback_uri = environ['twitter_callback_uri']
twitter_access_token = environ['twitter_access_token']
twitter_access_token_secret = environ['twitter_access_token_secret']

# Reddit Keys
reddit_client_secret = environ['reddit_client_secret']
reddit_client_id = environ['reddit_client_id']
reddit_username = environ['reddit_username']
reddit_user_agent = environ['reddit_user_agent']




caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

# app.config['SESSION_COOKIE_NAME'] = "Spotty Cookie"

# ----------------------------ERROR PAGE----------------------------

@app.errorhandler(404)
def error404(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def error500(error):
    return render_template('error.html'), 500


# ----------------------------Home and Authentication----------------------------

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-top-read',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        # return f'<h2><a href="{auth_url}">Sign in</a></h2>'
        return redirect(auth_url)

    # Step 4. Signed in, display data
    return render_template('index.html')


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


# ------------------------------ TOP ARTISTS PAGE -------------------------------------

@app.route('/artist_short_term')
def artist_short_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    

    top_artists  = sp.current_user_top_artists(limit=9, time_range='short_term')
    artist_info = []
    for artist in top_artists['items']: 
        name = artist['name']
        image = artist['images'][1]['url']
        followers = format(artist['followers']['total'], ',d')
        url = artist['id']
        artist_info.append([name, image, followers, url])
    return render_template('artist.html', artist_info = artist_info)


@app.route('/artist_medium_term')
def artist_medium_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    

    top_artists  = sp.current_user_top_artists(limit=9, time_range='medium_term')
    artist_info = []
    for artist in top_artists['items']: 
        name = artist['name']
        image = artist['images'][1]['url']
        followers = format(artist['followers']['total'], ',d')
        url = artist['id']
        artist_info.append([name, image, followers, url])
    return render_template('artist.html', artist_info = artist_info)


@app.route('/artist_long_term')
def artist_long_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    

    top_artists  = sp.current_user_top_artists(limit=9, time_range='long_term')
    artist_info = []
    for artist in top_artists['items']: 
        name = artist['name']
        image = artist['images'][1]['url']
        followers = format(artist['followers']['total'], ',d')
        url = artist['id']
        artist_info.append([name, image, followers, url])
    return render_template('artist.html', artist_info = artist_info)

# ------------------------------ ARTIST PERSONAL PAGE -------------------------------------
@app.route('/artist_personal/<artist_id>')
def artist_personal(artist_id):
    # Initialise sp variable
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)   
    
    # Get Artist Data - Image, Name, Followers, Genre, Redirect
    artist_data = sp.artists([artist_id])['artists'][0]
    name = artist_data['name']
    image = artist_data['images'][0]['url']
    followers = format(artist_data['followers']['total'], ',d')
    genres = artist_data['genres']
    redirect_url = artist_data['external_urls']['spotify']

    # Get Top Tracks
    track_list = []
    top_tracks = sp.artist_top_tracks(artist_id)['tracks']
    for track in top_tracks:
        track_name = track['name']
        track_id = track['id']
        track_url = track['external_urls']['spotify']
        track_image = track['album']['images'][0]['url']
        track_list.append([track_name, track_image, track_id])
    
    # Get Top albums
    albums = sp.artist_albums(artist_id, album_type='album')
    album_info = {}
    for item in albums['items']: 
        if item['name'] not in album_info:
            album_info[item['name']] = [item['release_date'], item['images'][0]['url']]
    album_info = list(album_info.items())

    # Artist Features
    features = list(sp.audio_features([track_url])[0].items())

    return render_template('artist_personal.html', track_list=track_list, name=name, followers=followers, image=image, genres=genres, redirect_url=redirect_url, album_info=album_info, features=features)

# ------------------------------ TOP TRACKS PAGE -------------------------------------

@app.route('/tracks_short_term')
def tracks_short_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)    
    results = sp.current_user_top_tracks(limit=20, time_range='short_term')
    track_info = []
    for track in results['items']:
        track_info.append([track['name'], track['album']['artists'][0]['name'], track['album']['images'][1]['url'], track['id']])
    return render_template('tracks.html', track_info = track_info)

@app.route('/tracks_medium_term')
def tracks_medium_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)    
    results = sp.current_user_top_tracks(limit=20, time_range='medium_term')
    track_info = []
    for track in results['items']:
        track_info.append([track['name'], track['album']['artists'][0]['name'], track['album']['images'][1]['url'], track['id']])
    return render_template('tracks.html', track_info = track_info)

@app.route('/tracks_long_term')
def tracks_long_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)    
    results = sp.current_user_top_tracks(limit=20, time_range='long_term')
    track_info = []
    for track in results['items']:
        track_info.append([track['name'], track['album']['artists'][0]['name'], track['album']['images'][1]['url'], track['id']])
    return render_template('tracks.html', track_info = track_info)



# ------------------------------ TRACK SINGLE PAGE -------------------------------------
@app.route('/track_single/<track_id>')
def track_single(track_id):
    # Initialise sp variable
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)   
    
    # Track Features
    try:
        features = list(sp.audio_features([track_id])[0].items())
    except:
        features = []

    # Get Track Data - Image, Artist, Name, Popularity, Artist_Data
    track_res = sp.track(track_id)
    track_image_curr = track_res['album']['images'][0]['url']
    artist_name = track_res['album']['artists'][0]['name']
    track_name_curr = track_res['name']
    track_popularity = track_res['popularity']/10


    artist_id = track_res['artists'][0]['id']
    artist_redirect_url = track_res['external_urls']['spotify']
    # artist_data = sp.artists([artist_id])['artists'][0]
    # artist_image = artist_data['images'][0]['url']
    # followers = artist_data['followers']['total']
    # genres = artist_data['genres']
    # redirect_url = artist_data['external_urls']['spotify']

    # Get Top Tracks by the Artist
    track_list = []
    top_tracks = sp.artist_top_tracks(artist_id)['tracks']
    for track in top_tracks:
        track_name = track['name']
        track_id = track['id']
        track_image = track['album']['images'][0]['url']
        track_list.append([track_name, track_image, track_id])



    return render_template('track_single.html', artist_id=artist_id, track_list=track_list, track_name_curr=track_name_curr, artist_name=artist_name, track_image_curr=track_image_curr, popularity=track_popularity, features=features, redirect_url=artist_redirect_url)



# ----------------------------TOP PAGE----------------------------

@app.route('/top')
def top():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    
    # top_tracks_df = get_top_tracks_data(sp)
    # top_tracks_df = pd.DataFrame(top_tracks_df)

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

    # fig = go.Figure()
    # fig.add_trace(go.Table(
    #     header=dict(values=['long_term', 'medium_term', 'short_term'],
    #                 fill_color='paleturquoise',
    #                 align='left'),
    #     cells=dict(values=[top_tracks_df.long_term, top_tracks_df.medium_term, top_tracks_df.short_term],
    #                fill_color='lavender',
    #                align='left'))
    #               )
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

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    header = 'Data on your favorite artists'
    description = ''
    return render_template('top.html', graphJSON2=graphJSON2, graphJSON3=graphJSON3)


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


# ----------------------------TWITTER PAGE----------------------------


@app.route('/twitter')
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


# ----------------------------REDDIT PAGE----------------------------



@app.route('/reddit')
def reddit():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager) 
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
    results = sp.current_user_top_artists(time_range='medium_term', limit=8)
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


# ----------------------------RECOMMENDATIONS PAGE----------------------------

@app.route('/spotify_rec')
def spotify_rec():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager) 
    
    info_list = []

    results = sp.current_user_top_artists(time_range='short_term', limit=5)
    artist_list = []
    for item in results['items']:
        seed_id = item['id']
        recommendations = sp.recommendations(seed_artists=[seed_id], limit=3)
        for item in recommendations['tracks']:
            track = item['name']
            image = item['album']['images'][1]['url']
            artist = item['album']['artists'][0]['name']
            artist_id = item['album']['artists'][0]['id']
            # album = item['album']['name']
            info_list.append([track, image, artist, artist_id])
    return render_template('spotify_rec.html', info_list=info_list)


# ----------------------------USER COLLECTION PAGE----------------------------------



@app.route('/user_collection')
def user_collection():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    # mongo = current_app.config['mongo']
    collection = mongo.db.userTracks
    track = request.args.get('track')
    artist = request.args.get('artist')
    

    # Initial Run - with no input
    if track == None or artist == None:
        track_df = create_df(collection)
        graphJSON2 = plot_scatter(track_df)
        track_list = []
        for row in track_df.iterrows():
            track_name = row[1][0]
            artist_name = row[1][1]
            artist_id = row[1][4]
            image = row[1][5]
            final = [track_name, artist_name, image, artist_id]
            if final not in track_list:
                track_list.append([track_name, artist_name, image, artist_id])
        return render_template('user_collection.html', graphJSON=graphJSON2, track_list=track_list)
    # Secondary Run - with some input provided
    else:
        artist_id = sp.search(track)['tracks']['items'][0]['album']['artists'][0]['id']
        image = sp.search(track)['tracks']['items'][0]['album']['images'][1]['url']
        curr_time = int(time.time())
        # Check if data is new or existing and update collection
        update_db(collection, track, artist, curr_time, artist_id, image)
        track_df = create_df(collection)
        graphJSON2 = plot_scatter(track_df)
        track_list = []
        for row in track_df.iterrows():
            track_name = row[1][0]
            artist_name = row[1][1]
            artist_id = row[1][4]
            image = row[1][5]
            final = [track_name, artist_name, image, artist_id]
            if final not in track_list:
                track_list.append([track_name, artist_name, image, artist_id])
        return render_template('user_collection.html', graphJSON=graphJSON2, track_list=track_list)


def plot_scatter(track_df):
    hover_text = []
    bubble_size = []

    for index, row in track_df.iterrows():
        hover_text.append(('song name: {country}<br>' +
                           'artist: {lifeExp}<br>' +
                           'release: {gdp}<br>' +
                           'count: {year}').format(country=row['song_name'],
                                                   lifeExp=row['artist_name'],
                                                   gdp=row['suggested_date'],
                                                   year=row['count']))
        # bubble_size.append(math.sqrt(row['song_duration']))
        # bubble_size.append(100)
    track_df['text'] = hover_text
    # track_df['size'] = bubble_size
    # sizeref = 2.*max(track_df['size'])
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


def update_db(collection, track, artist, curr_time, artist_id, image):
    query = collection.find(
        {'track_check': track.lower(), 'artist_check': artist.lower()})

    count = query.count()
    if count == 0:
        collection.insert_one({'track': track, 'artist': artist, 'time': curr_time,
                              'track_check': track.lower(), 'artist_check': artist.lower(), 'count': 1, 'artist_id':artist_id, 'image': image})
    else:
        for result in query:
            id = result['_id']
        collection.find_one_and_update({'_id': id}, {'$inc': {'count': 1}})


def create_df(collection):
    song_name = []
    artist_name = []
    suggested_date = []
    song_count = []
    artist_id = []
    image = []
    for result in collection.find({}):
        song_name.append(result['track'])
        artist_name.append(result['artist'])
        time = datetime.utcfromtimestamp(
            result['time']).strftime('%Y-%m-%d %H:%M:%S')
        suggested_date.append(time)
        song_count.append(result['count'])
        artist_id.append(result['artist_id'])
        image.append(result['image'])

    df = pd.DataFrame({
        'song_name': song_name,
        'artist_name': artist_name,
        'suggested_date': suggested_date,
        'count': song_count,
        'artist_id': artist_id,
        'image': image
    })
    return df


# ----------------------------WORLD TRENDS----------------------------------
@app.route('/world_trends')
def world_trends():
    collection = mongo.db.csv_import
    shazam_data = collection.find({})
    for i in shazam_data:
        dat = dict(i)
    df = pd.DataFrame(dat)
    data = []
    for row in df.iterrows():
        data.append([ row[1][4].split(',')[0][2:-1], row[1][3], row[1][2]])

    return render_template('world_trends.html', data=json.dumps(data))


# ----------------------------CSV TRANSFER----------------------------------

@app.route('/csv_transfer')
def csv_transfer():
    """ 
    sending the 'world trends' csv file to mongo_db. This should run once a day to keep the data updated.
    
    Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    collection = mongo.db.csv_import
    try:
        # create_charts()
        collection.remove({})
        df = pd.read_csv('./shazam.csv')
        df.to_json('yourjson.json')                               # saving to json file
        jdf = open('yourjson.json').read()                        # loading the json file 
        data = json.loads(jdf)
        collection.insert_one(data)
    except:
        return "Today's Data Added to Mongo Collection"
    return "Today's Data Added to Mongo Collection"


def create_charts():
    charts_list = "https://shazam.p.rapidapi.com/charts/list"

    charts_list_headers = {
        'x-rapidapi-key': "d78ca9f758msh31ad154b2fe50a8p12fbc9jsnabb8cabd4076",
        'x-rapidapi-host': "shazam.p.rapidapi.com"
        }

    charts_list_response = requests.request("GET", charts_list, headers=charts_list_headers)

    country_list = []
    city_list = []
    top10 = []
    coords_lat = []
    coords_lon = []

    for country_dict in charts_list_response.json()['countries']:
        for city in country_dict['cities']:
            # if len(city_list) < 4:
            try:
                lat, lon = get_lat_lon(city['name'])
                country_list.append(country_dict['name'])
                city_list.append(city['name'])
                coords_lat.append(lat)
                coords_lon.append(lon)
                top_10_json = get_top10_json(city['listid']).json()
                top10.append(get_top10_names(top_10_json))
            except:
                continue
            # else:
            #     break


    daily_df = pd.DataFrame({'country': country_list, 'city': city_list,"lat": coords_lat, 'lon': coords_lon ,'top10': top10})
    daily_df.to_csv('./shazam.csv')

def get_top10_json(list_id):
    url = "https://shazam.p.rapidapi.com/charts/track"

    querystring = {"locale":"en-US","listId":list_id,"pageSize":"20","startFrom":"0"}

    headers = {
        'x-rapidapi-key': "d78ca9f758msh31ad154b2fe50a8p12fbc9jsnabb8cabd4076",
        'x-rapidapi-host': "shazam.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def get_top10_names(top_10_json):
    tracks_dict = top_10_json['tracks']
    names = []
    for track in tracks_dict:
        names.append((track['title'] + ' - '+ track['subtitle']))
    return names


def get_lat_lon(name):
    f = { 'name' : name}
    formatted_name = urllib.parse.urlencode(f)
    # print(formatted_name)
    response = requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?access_token=pk.eyJ1IjoiaGFyc2gtaiIsImEiOiJja3JraHRmMnEzbnA1MndwOGI2OTY1enNrIn0.Lrx1G8lFIKLt_7OsC6ow7g".format(formatted_name[5:]))
    return response.json()['features'][0]['bbox'][1], response.json()['features'][0]['bbox'][0]


# ----------------------------CONTACT PAGE----------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        collection = mongo.db.contact
        collection.insert_one({'name': name,
                               'email': email, 'message': message})
        return render_template('index.html')
    else:
        return render_template('index.html')



# ----------------------------End----------------------------


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 5000).split(":")[-1])))



