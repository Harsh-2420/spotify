import ast
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import pickle
import pdb
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
    # genres_top_count = pd.Series(genres_top_count).sort_values(ascending=False)
    genres_top_count = {k: v for k, v in sorted(
        genres_top_count.items(), key=lambda item: item[1], reverse=True)}
    return genres_top_count


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


top_artist_df = create_top_artist_data(sp)
top_genres_short = top_genres(top_artist_df)
sunburst_data = create_sunburst_data(top_artist_df, top_genres_short)

# print(top_artist_df)
# print(top_genres_short)
print(sunburst_data)
