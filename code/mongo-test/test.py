from pymongo import MongoClient
import time

cluster = MongoClient(
    "mongodb+srv://admin:asdfgh09@cluster0.h6kse.mongodb.net/spotty?retryWrites=true&w=majority")
db = cluster["spotty"]
collection = db['userTracks']
curr_time = time.time()


def update_db(collection, track, artist, curr_time):
    query = collection.find(
        {'track_check': track.lower(), 'artist_check': artist.lower()})

    count = query.count()
    if count == 0:
        collection.insert_one({'track': track, 'artist': artist, 'time': curr_time,
                              'track_check': track.lower(), 'artist_check': artist.lower(), 'count': count})
    else:
        for result in query:
            curr_count = result['count']
        collection.update_one({'track_check': track.lower()}, {
            'artist_check': artist.lower}, {'$set': {'count': curr_count}})


update_db(collection, 'Ninety', 'Jaden', curr_time)
