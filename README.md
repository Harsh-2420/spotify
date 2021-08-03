# Spotty - Music Recommendation


<!-- Python -->
<img align="left" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />        

<!-- Spotify -->
<img align="left" src="https://img.shields.io/badge/Spotify-1ED760?&style=for-the-badge&logo=spotify&logoColor=white" />        

<!-- Flask -->
<img align="left" src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />        

<!-- Tensorflow -->
<img align="left" src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=TensorFlow&logoColor=white" />        

<!-- SQL -->
<img align="left" src="https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white" /> 

<!-- SQL -->
<img align="left" src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" /> 

<!-- Heroku -->
<img align="left" src="https://img.shields.io/badge/Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" /> 

</br>
</br>
</br>

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


</br>

## Project Details

Data Points Used:

- Artist Data (like, genres, popularity, etc)
- Track Data (like, loudness, tempo, valence, etc)

I have performed the following tasks using the extracted data:
Task 1:
- Data Analysis and Visualisation with data since 1922.
- Time Series Analysis of the most popular artists and tracks

Task 2:
- Building a content-based recommendation system to recommend artists to users
- Deployed this model using Flask and Heroku.

Task 3:
- Generating unique insights about each user's Spotify history and displaying them using Plotly.
- Performed ETL on Reddit and Twitter API to get data from artists and display popularity on social media.

Task 4:
- Built a front-end UI for the project 
- Created an entire data pipeline and performed cron jobs while using MongoDB

### In Progress
Task 5:
- Improvements to the recommendation system by adding NLP and Audio Recognition using parallel CNN-RNN.
