# Spotify Recommendation
Used the [Spotify](https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks) dataset from Kaggle which is data on all songs available on Spotify from 1922 - 2021. This data includes details on artists and tracks with several variables being tracked for both.
These variables include: 
- genres and popularity (for artists)
- artists, loudness, tempo, valence, popularity, acousticness, danceability, etc (for tracks)

I have performed the following tasks on this dataset:
Task 1:
- Data Analysis and Visualisation on the dataset
- Time Series Analysis of the most popular artists and tracks

Task 2:
- Building a recommendation model using content based recommendation
-  This model takes an artist as an input and recommends other artists similar to the input
-  Task 2a:
  -  Expanded the model to take in multiple artists with different weights and recommend based on these weights.
-  Task 2b:
  -  Deployed the model on Flask and currently working on deploying it on AWS/Heroku

# In Progress
Task 3:
- Building a recommendation model that can take a song as an input and recommend similar songs.
- Expanding this model to take several songs as input.

Task 4:
- Connect to the Spotify API so that the model can read in a user's frequented artists/songs and recommend new ones.
