from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://admin:asdfgh09@cluster0.h6kse.mongodb.net/spotty?retryWrites=true&w=majority")
db = cluster["spotty"]
collection = db['userTracks']

for x in collection.find({}):
    print(x)
