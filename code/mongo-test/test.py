from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://admin:asdfgh09@cluster0.h6kse.mongodb.net/spotty?retryWrites=true&w=majority")
# cluster = MongoClient('localhost', 27017)
db = cluster["spotty"]
collection = db['spotty_user_collection']

collection.insert_one({'name': "JJ"})
# print(collection)
