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
with open('./pickle/indices', 'rb') as f:
    indices = pickle.load(f)
with open('./pickle/names', 'rb') as f:
    names = pickle.load(f)
with open('./pickle/cosine_sim', 'rb') as f:
    cosine_similarities = pickle.load(f)


def artist_recommend(name):
    idx = indices[name]
    sim_scores = list(enumerate(cosine_similarities[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    artist_indices = [i[0] for i in sim_scores]
    return names.iloc[artist_indices]


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
def upload():
    if request.method == "POST":
        name = request.form['text']
        preds = artist_recommend(name)
        return str(preds)
    return 'upload func ran'


if __name__ == '__main__':
    app.run(debug=True)
