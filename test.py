import ast
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import pickle
from git_ignore.config import *

scope = 'user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:5000",
                                               scope=scope))
results = sp.current_user_top_artists(time_range='short_term', limit=50)
# print(results['items'][1])


def create_top_artist_data(sp):
    results = sp.current_user_top_artists(time_range='short_term', limit=50)
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
    genres, artists, values = [], [], []
    for i, row in df.iterrows():
        for genre, value in zip(top_genres.index, top_genres.values):
            if genre in row['genres']:
                genres.append(genre)
                values.append(str(value))
                artists.append(row['name'])

    dataframe = pd.DataFrame()
    dataframe['artist'] = artists
    dataframe['genres'] = genres
    dataframe['values'] = values
    return dataframe


top_artist_df = create_top_artist_data(sp)
top_genres_short = top_genres(top_artist_df)
sunburst_data = create_sunburst_data(top_artist_df, top_genres_short)

print(sunburst_data)
