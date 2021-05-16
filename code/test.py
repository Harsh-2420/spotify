import ast
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import pickle
import pdb
from git_ignore.config import *

scope = "user-top-read user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:5000",
                                               scope=scope))
# results = sp.current_user_top_artists(time_range='long_term', limit=10)
# id = results['items'][1]['id']


results = sp.current_user_top_artists(time_range='long_term', limit=10)
name = []
popularity = []
genres = []
followers = []
for item in results['items']:
    top_id = item['id']
    recs = sp.artist_related_artists(top_id)
    for rec in recs['artists']:
        name.append(rec['name'])
        popularity.append(rec['popularity'])
        genres.append(rec['genres'])
        followers.append(rec['followers']['total'])
df = pd.DataFrame()
df['name'] = name
df['popularity'] = popularity
df['genres'] = genres
df['followers'] = followers


print(name)
