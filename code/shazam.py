import pandas as pd
import requests

charts_list = "https://shazam.p.rapidapi.com/charts/list"

charts_list_headers = {
    'x-rapidapi-key': "d78ca9f758msh31ad154b2fe50a8p12fbc9jsnabb8cabd4076",
    'x-rapidapi-host': "shazam.p.rapidapi.com"
    }

charts_list_response = requests.request("GET", charts_list, headers=charts_list_headers)


def get_top10_json(list_id):
    url = "https://shazam.p.rapidapi.com/charts/track"

    querystring = {"locale":"en-US","listId":list_id,"pageSize":"20","startFrom":"0"}

    headers = {
        'x-rapidapi-key': "d78ca9f758msh31ad154b2fe50a8p12fbc9jsnabb8cabd4076",
        'x-rapidapi-host': "shazam.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


# city_name = charts_list_response.json()['countries'][14]['cities']
# listid = charts_list_response.json()['countries'][14]['cities'][0]['listid']








def get_top10_names(top_10_json):
    tracks_dict = top_10_json['tracks']
    names = []
    for track in tracks_dict:
        names.append((track['title'] + ' - '+ track['subtitle']))
    return names


country_list = []
city_list = []
top10 = []

for country_dict in charts_list_response.json()['countries']:
    if country_dict['name'] == 'India':
        for city in country_dict['cities']:
            if len(city_list) < 4:
                country_list.append('India')
                city_list.append(city['name'])
                top_10_json = get_top10_json(city['listid']).json()
                top10.append(get_top10_names(top_10_json))
                print(city_list)
            else:
                break
        break


daily_df = pd.DataFrame({'country': country_list, 'city': city_list,'top10': top10})