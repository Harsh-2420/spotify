# import time
# from flask import Flask, request, url_for, redirect, session, render_template
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from git_ignore.config import *
# import pandas as pd
# import dash
# import dash_table
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go
# import plotly.express as px
# import plotly.figure_factory as ff
# import json
# from datetime import datetime


# app = Flask(__name__)

# app.secret_key = "spotty"
# app.config['SESSION_COOKIE_NAME'] = "Harsh Cookie"
# TOKEN_INFO = "token_info"


# @app.route('/')
# def login():
#     sp_oauth = create_spotify_ouath()
#     auth_url = sp_oauth.get_authorize_url()
#     return redirect(auth_url)


# @app.route('/redirect')
# def redirectPage():
#     sp_oauth = create_spotify_ouath()
#     session.clear()
#     code = request.args.get('code')
#     token_info = sp_oauth.get_access_token(code)
#     session[TOKEN_INFO] = token_info
#     return redirect(url_for('getTracks', _external=True))


# @app.route('/getTracks')
# def getTracks():
#     try:
#         token_info = get_token()
#     except:
#         print("user not logged in")
#         return redirect('/')
#     sp = spotipy.Spotify(auth=token_info['access_token'])

#     song_name, song_duration, song_popularity, release_date, artist_name = get_top_songs_over_release_date_vs_popularity(
#         sp)
#     bar = plot_top_songs_over_release_date_vs_popularity(
#         song_name, song_duration, song_popularity, release_date, artist_name)
#     top_tracks_df = get_top_tracks_data(sp)
#     top_artists_df = get_top_artists_data(sp)
#     return render_template('base.html',
#                            tables=[top_artists_df.to_html(
#                                classes='data'), top_tracks_df.to_html(classes='data')],
#                            titles=[top_artists_df.columns.values, top_tracks_df.columns.values], plot=bar)


# def get_token():
#     token_info = session.get(TOKEN_INFO, None)
#     if not token_info:
#         raise "exception"
#     now = int(time.time())
#     is_expired = token_info['expires_at'] - now < 60
#     if (is_expired):
#         sp_oauth = create_spotify_ouath()
#         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
#     return token_info


# def create_spotify_ouath():
#     return SpotifyOAuth(
#         client_id=client_id,
#         client_secret=client_secret,
#         redirect_uri=url_for('redirectPage', _external=True),
#         scope="user-library-read")


# def get_top_tracks_data(sp):
#     ranges = ['short_term', 'medium_term', 'long_term']
#     tracks = {}
#     for sp_range in ranges:
#         tracks[sp_range] = []
#         results = sp.current_user_top_tracks(time_range=sp_range, limit=20)
#         for i, item in enumerate(results['items']):
#             val = item['name']
#             tracks[sp_range].append(val)
#     top_tracks_df = pd.DataFrame(tracks)
#     return top_tracks_df


# def get_top_artists_data(sp):
#     ranges = ['short_term', 'medium_term', 'long_term']
#     artists = {}
#     for sp_range in ranges:
#         artists[sp_range] = []
#         results = sp.current_user_top_artists(time_range=sp_range, limit=15)
#         for i, item in enumerate(results['items']):
#             val = item['name']
#             artists[sp_range].append(val)
#     top_artists_df = pd.DataFrame(artists)
#     return top_artists_df


# def get_top_albums(sp):
#     ranges = ['short_term', 'medium_term', 'long_term']
#     albums = {}
#     for sp_range in ranges:
#         albums[sp_range] = []
#         results = sp.current_user_top_tracks(time_range=sp_range, limit=20)
#         for i, item in enumerate(results['items']):
#             val = item['album']['name']
#             albums[sp_range].append(val)
#     top_albums_df = pd.DataFrame(tracks)
#     return top_albums_df


# def get_top_songs_over_release_date_vs_popularity(sp):

#     song_name = []
#     release_date = []
#     song_popularity = []
#     song_duration = []
#     artist_name = []

#     # tracks['short_term'] = []
#     results = sp.current_user_top_tracks(time_range="short_term", limit=20)
#     for i, item in enumerate(results['items']):
#         song_name.append(item['name'])
#         date = sp.album(item["album"]["external_urls"]["spotify"])[
#             'release_date']
#         release_date.append(datetime.strptime(date, "%Y-%m-%d").date())
#         song_popularity.append(item['popularity'])
#         song_duration.append(item['duration_ms'])
#         artist_name.append(item['artists'][0]['name'])

#     # df = pd.DataFrame(
#     # {'song_name': song_name,
#     #  'song_duration': song_duration,
#     #  'song_popularity': song_popularity,
#     #  'release_date': release_date,
#     #  'artist_name': artist_name
#     # })

#     return song_name, song_duration, song_popularity, release_date, artist_name


# def plot_top_songs_over_release_date_vs_popularity(song_name, song_duration, song_popularity, release_date, artist_name):

#     hover_text = []
#     bubble_size = []

#     # for index, row in df_2007.iterrows():
#     # hover_text.append(('Country: {country}<br>'+
#     #                 'Life Expectancy: {lifeExp}<br>'+
#     #                 'GDP per capita: {gdp}<br>'+
#     #                 'Population: {pop}<br>'+
#     #                 'Year: {year}').format(country=row['country'],
#     #                                         lifeExp=row['lifeExp'],
#     #                                         gdp=row['gdpPercap'],
#     #                                         pop=row['pop'],
#     #                                         year=row['year']))
#     for k in range(len(song_name)):
#         hover_text.append(('Song Name: {song_name}<br>' +
#                            'Artist Name: {artist_name}'
#                            ).format(song_name=song_name[k],
#                                     artist_name=artist_name[k],
#                                     ))
#     bubble_size = song_duration
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=release_date, y=song_popularity,
#         name=song_name, text=hover_text,
#         marker_size=bubble_size,
#     ))
#     fig.update_traces(mode='markers', marker=dict(sizemode='area',
#                                                   sizeref=sizeref, line_width=2))

#     fig.update_layout(
#         title='Life Expectancy v. Per Capita GDP, 2007',
#         xaxis=dict(
#             title='GDP per capita (2000 dollars)',
#             gridcolor='white',
#             type='log',
#             gridwidth=2,
#         ),
#         yaxis=dict(
#             title='Life Expectancy (years)',
#             gridcolor='white',
#             gridwidth=2,
#         ),
#         paper_bgcolor='rgb(243, 243, 243)',
#         plot_bgcolor='rgb(243, 243, 243)',
#     )

#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     return graphJSON


# if __name__ == "__main__":
#     app.run(debug=True)
