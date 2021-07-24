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

@app.route('/artist')
def artist():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    
    top_artists  = sp.current_user_top_artists(limit=9)
    artist_info = []
    for artist in top_artists['items']: 
        name = artist['name']
        image = artist['images'][1]['url']
        followers = artist['followers']['total']
        url = artist['id']
        artist_info.append([name, image, followers, url])
        # artist_dict[artist['name']] = [artist['images'][1]['url'], artist['followers']['total'], artist['genres'], artist['external_urls']['spotify'] ]
    return render_template('artist.html', artist_info = artist_info)


# ------------------------------ ARTIST PERSONAL PAGE -------------------------------------
@app.route('/artist_personal/<url>')
def artist_personal(url):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(auth_manager=auth_manager)   
    
    track_list = []
    top_tracks = sp.artist_top_tracks(url)['tracks']
    for track in top_tracks:
        track_list.append(track['name'])
    return render_template('artist_personal.html', track_list=track_list)
    
    # for artist in artist_dict.values():
    #     top = sp.artist_top_tracks(url)['tracks']
    #     for track in top:
    #         url = track['external_urls']['spotify']
    #         artist_top_tracks_dict[track['name']] = url
    #         break
    #     break
    # artist_top_tracks_dict 
    # pass


# ----------------------------TOP PAGE----------------------------

@app.route('/top')
def top():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)    
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
    return render_template('top.html', graphJSON=graphJSON, graphJSON2=graphJSON2, graphJSON3=graphJSON3)


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


# ----------------------------RECOMMENDATIONS PAGE----------------------------

@app.route('/spotify_rec')
def spotify_rec():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager) 

    df = create_related_artist_df(sp)

    fig = go.Figure()
    fig.add_trace(go.Table(
        header=dict(values=['Name', 'Popularity', 'Total Followers', 'Recommendation Based On', 'Genres'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.name, df.popularity, df.followers, df.based_on, df.genres],
                   fill_color='lavender',
                   align='left'))
                  )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = ""
    description = ''
    return render_template('spotify_rec.html', graphJSON=graphJSON, header=header, description=description)


def create_related_artist_df(sp):
    results = sp.current_user_top_artists(time_range='long_term', limit=10)
    name = []
    popularity = []
    genres = []
    followers = []
    based_on = []
    for item in results['items']:

        top_id = item['id']
        recs = sp.artist_related_artists(top_id)

        for rec in recs['artists']:
            based_on.append(item['name'])
            name.append(rec['name'])
            popularity.append(rec['popularity'])
            genres.append(rec['genres'])
            followers.append(rec['followers']['total'])
    df = pd.DataFrame()
    df['name'] = name
    df['popularity'] = popularity
    df['genres'] = genres
    df['followers'] = followers
    df['based_on'] = based_on
    # df.loc[df.astype(str).drop_duplicates(subset='genres', keep='first').index]
    return df


# ----------------------------USER COLLECTION PAGE----------------------------------



@app.route('/user_collection')
def user_collection():
    # mongo = current_app.config['mongo']
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


def update_db(collection, track, artist, curr_time):
    query = collection.find(
        {'track_check': track.lower(), 'artist_check': artist.lower()})

    count = query.count()
    if count == 0:
        collection.insert_one({'track': track, 'artist': artist, 'time': curr_time,
                              'track_check': track.lower(), 'artist_check': artist.lower(), 'count': 1})
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
        time = datetime.utcfromtimestamp(
            result['time']).strftime('%Y-%m-%d %H:%M:%S')
        suggested_date.append(time)
        song_count.append(result['count'])

    df = pd.DataFrame({
        'song_name': song_name,
        'artist_name': artist_name,
        'suggested_date': suggested_date,
        'count': song_count

    })
    return df



# ----------------------------CONTACT PAGE----------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        collection = mongo.db.contact
        collection.insert_one({'name': name, 'phone': phone,
                               'email': email, 'message': message})
        return render_template('index.html')
    else:
        return render_template('index.html')



# ----------------------------End----------------------------


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 5000).split(":")[-1])))



