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
results = sp.search('A Day At A Time')

# for i, item in enumerate(results['items']):
#     print(item['artists'])
for result in results['tracks']['items']:
    print(result["album"]['artists'][0]['name'])
