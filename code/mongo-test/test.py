from pymongo import MongoClient
import time
from datetime import datetime
import pandas as pd
import os

mongo_uri = os.environ.get('MONGO_URI')
cluster = MongoClient(mongo_uri)
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
            id = result['_id']
        collection.find_one_and_update({'_id': id}, {'$inc': {'count': 1}})


def create_df(collection):
    song_name = []
    artist_name = []
    suggested_date = []
    song_count = []
    for result in collection.find({}):
        song_name.append(result['track'])
        artist_name.append(result['artist'])
        time = datetime.utcfromtimestamp(
            result['time']).strftime('%Y-%m-%d %H:%M:%S')
        suggested_date.append(time)
        song_count.append(result['count'])

    df = pd.DataFrame({
        'song_name': song_name,
        'artist_name': artist_name,
        'suggested_date': suggested_date,
        'count': song_count
    })
    return df


# update_db(collection, 'KOD', 'J.Cole', curr_time)
track_df = create_df(collection)
print(track_df)
