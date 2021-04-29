import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from config import *

scope = 'user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:5000",
                                               scope=scope))

results = sp.current_user_top_tracks(time_range='short_term', limit=50)
print(results['items'][1]['artists'][0]['name'])


# Get Release Date:
# release_date = sp.album(results['items'][1]["album"]["external_urls"]["spotify"])['release_date']
# release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
# print(type(release_date))
# print(release_date)


# ranges = ['short_term', 'medium_term', 'long_term']
# artists = {}
# for sp_range in ranges:
#     artists[sp_range] = []
#     results = sp.current_user_top_artists(time_range=sp_range, limit=18)
#     for i, item in enumerate(results['items']):
#         val = item['name']
#         artists[sp_range].append(val)
# top_artists_df = pd.DataFrame(artists)
# print(top_artists_df)
