# Spotty - Music Recommendation

Designed a Flask App with Spotify API to recommend music to users using TFIDF vectorizer and performed Exploratory Data Analysis with Plotly. 
Furthermore, created sentiment analysis with Twitter API and gave the user a popularity score of their favorite artists. 
Containerized the model pipeline and webapp using Docker and hosted the backend on AWS Cloud using EC2 and S3.

## Exploring the Website!

Check out the website at [Spotty](http://spotty-music.herokuapp.com/). Click the link and log into your Spotify account and continue exploring! The tasks I performed in this project are at the end of the Readme file.

## Running it locally

1. Clone the repo
```
git clone https://github.com/Harsh-2420/spotify.git
```

2. Install packages
```
cd code
pip install -r requirements.txt
```
3. Run the app
```
flask run
```
4. Go to localhost:5000


## Tasks

Variables using the API:

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
  -  Built the model using Flask and deployed it on Heroku.

### In Progress
Task 3:
- Building a recommendation model that can take a song as an input and recommend similar songs.
- Expanding this model to take several songs as input.

Task 4:
- Connect to the Spotify API so that the model can read in a user's frequented artists/songs and recommend new ones.
