# from flask import Flask, render_template, jsonify, request, url_for
# import numpy as np
# import matplotlib.pyplot as plt
# import tensorflow as tf
# from tensorflow import keras
# import os
# import pickle

# # Define Flask app
# app = Flask(__name__)

# # Load the trained model
# with open('./pickle/cos_sim_results', 'rb') as f:
#     results = pickle.load(f)


# def _recommend(item_id, num):
#     recs = results[item_id][:num]
#     preds = {}
#     for pair in recs:
#         preds[pair[1]] = pair[0]
#     return preds


# def get_similar_artists_multiple(artists, num=10):
#     dict_similar = {}
#     for artist, weight in artists.items():
#         dict_similar[artist] = _recommend(artist, num)
#     artists_all = []
#     for artist, similar_artists in dict_similar.items():
#         artists_all.append(list(similar_artists.keys()))
#     artists_unique = np.unique(artists_all).tolist()
#     artists_dict = {artist: 0 for artist in artists_unique}
#     for artist, similar_artists in dict_similar.items():
#         for similar_artist, score in similar_artists.items():
#             artists_dict[similar_artist] += artists[artist] * score
#     return list({k: v for k, v in sorted(artists_dict.items(), key=lambda item: item[1], reverse=True) if k not in artists}.keys())[0:num]


# @app.route("/", methods=['GET'])
# def index():
#     return render_template('index.html')


# @app.route("/predict", methods=['POST'])
# def upload():
#     if request.method == "POST":
#         num = int(request.form['rec'])
#         names = request.form['text'].split(',')
#         weights = request.form['weight'].split(',')
#         artists = {}
#         for k, name in enumerate(names):
#             artists[name.strip()] = int(weights[k])
#         preds = get_similar_artists_multiple(artists, num)
#         return str(preds)
#     return 'upload func ran'


# if __name__ == '__main__':
#     app.run(debug=True)
