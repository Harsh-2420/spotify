from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://admin:asdfgh09@cluster0.h6kse.mongodb.net/spotty?retryWrites=true&w=majority'
mongo = PyMongo(app)


@app.route('/')
def index():
    usr = mongo.db.usr
    usr.insert_one({'name': 'JJ'})
    return 'Added'


if __name__ == '__main__':
    app.run(debug=True)
