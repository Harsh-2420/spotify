# from flask import render_template, Blueprint, request
# import pickle
# import numpy as np


# recommend_ = Blueprint('recommend', __name__, template_folder='templates')


# @recommend_.route('/recommend/', methods=['GET'])
# def recommend():
#     return render_template('recommend.html')


# @recommend_.route("/predict/", methods=['POST'])
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


# # recommendationPage
# # Load the trained model
# with open('./pickle/cos_sim_results', 'rb') as f:
#     results = pickle.load(f)


# def recommend_artist(item_id, num):
#     recs = results[item_id][:num]
#     preds = {}
#     for pair in recs:
#         preds[pair[1]] = pair[0]
#     return preds


# def get_similar_artists_multiple(artists, num=10):
#     dict_similar = {}
#     for artist, weight in artists.items():
#         dict_similar[artist] = recommend_artist(artist, num)
#     artists_all = []
#     for artist, similar_artists in dict_similar.items():
#         artists_all.append(list(similar_artists.keys()))
#     artists_unique = np.unique(artists_all).tolist()
#     artists_dict = {artist: 0 for artist in artists_unique}
#     for artist, similar_artists in dict_similar.items():
#         for similar_artist, score in similar_artists.items():
#             artists_dict[similar_artist] += artists[artist] * score
#     return list({k: v for k, v in sorted(artists_dict.items(), key=lambda item: item[1], reverse=True) if k not in artists}.keys())[0:num]
