from flask import Flask, render_template, jsonify, request, url_for
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
import os
# from werkzeug.utils import secure_filename
# from keras.preprocessing.image import load_img, img_to_array, array_to_img, save_img
# from PIL import Image, ImageOps
import pickle

# Define Flask app
app = Flask(__name__)

# Load the trained model
with open('./pickle/cos_sim_results', 'rb') as f:
    results = pickle.load(f)


def _recommend(item_id, num):
    recs = results[item_id][:num]
    preds = {}
    for pair in recs:
        preds[pair[1]] = pair[0]
    return preds


def get_similar_artists_multiple(artists, num=10):
    dict_similar = {}
    for artist, weight in artists.items():
        dict_similar[artist] = _recommend(artist, num)
    artists_all = []
    for artist, similar_artists in dict_similar.items():
        artists_all.append(list(similar_artists.keys()))
    artists_unique = np.unique(artists_all).tolist()
    artists_dict = {artist: 0 for artist in artists_unique}
    for artist, similar_artists in dict_similar.items():
        for similar_artist, score in similar_artists.items():
            artists_dict[similar_artist] += artists[artist] * score
    return list({k: v for k, v in sorted(artists_dict.items(), key=lambda item: item[1], reverse=True) if k not in artists}.keys())[0:num]


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
def upload():
    if request.method == "POST":
        num = int(request.form['rec'])
        names = request.form['text'].split(',')
        weights = request.form['weight'].split(',')
        artists = {}
        for k, name in enumerate(names):
            artists[name.strip()] = int(weights[k])
        preds = get_similar_artists_multiple(artists, num)
        return str(preds)
    return 'upload func ran'


# @app.route('/authorize')
# def authorize():
#   client_id = app.config['CLIENT_ID']
#   redirect_uri = app.config['REDIRECT_URI']
#   scope = app.config['SCOPE']
#   state_key = createStateKey(15)
#   session['state_key'] = state_key

#   authorize_url = 'https://accounts.spotify.com/en/authorize?'
#   params = {'response_type': 'code', 'client_id': client_id,
#             'redirect_uri': redirect_uri, 'scope': scope,
#             'state': state_key}
#   query_params = urlencode(params)
#   response = make_response(redirect(authorize_url + query_params))
#   return response


#   def getToken(code):
#   token_url = 'https://accounts.spotify.com/api/token'
#   authorization = app.config['AUTHORIZATION']
#   redirect_uri = app.config['REDIRECT_URI']
#   headers = {'Authorization': authorization,
#              'Accept': 'application/json',
#              'Content-Type': 'application/x-www-form-urlencoded'}
#   body = {'code': code, 'redirect_uri': redirect_uri,
#           'grant_type': 'authorization_code'}
#   post_response = requests.post(token_url,headers=headers,data=body)
#   if post_response.status_code == 200:
#     pr = post_response.json()
#     return pr['access_token'], pr['refresh_token'], pr['expires_in']
#   else:
#     logging.error('getToken:' + str(post_response.status_code))
#     return None

# def makeGetRequest(session, url, params={}):
#   headers = {"Authorization": "Bearer {}".format(session['token'])}
#   response = requests.get(url, headers=headers, params=params)
#   if response.status_code == 200:
#     return response.json()
#   elif response.status_code == 401
#        and checkTokenStatus(session) != None:
#     return makeGetRequest(session, url, params)
#   else:
#     logging.error('makeGetRequest:' + str(response.status_code))
#     return None

# def checkTokenStatus(session):
#   if time.time() > session['token_expiration']:
#     payload = refreshToken(session['refresh_token'])
#   if payload != None:
#     session['token'] = payload[0]
#     session['token_expiration'] = time.time() + payload[1]
#   else:
#     logging.error('checkTokenStatus')
#     return None
#   return "Success"

if __name__ == '__main__':
    app.run(debug=True)
