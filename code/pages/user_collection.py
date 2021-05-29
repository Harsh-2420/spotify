from flask import render_template, Blueprint, current_app, request
import numpy as np
import pandas as pd
import tweepy
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from os import environ
import re


user_collection_ = Blueprint(
    'user_collection', __name__, template_folder='templates')


@user_collection_.route('/user_collection')
def user_collection():
    key = request.args.get('key')
    return render_template('user_collection.html')
