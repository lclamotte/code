from constants import LEAGUE_URL

import requests

def get_league_json():
    league_response = requests.get(LEAGUE_URL)
    if league_response.status_code == 200:
        league_json = league_response.json()
    else:
        raise Exception(f"Failed to fetch league details: {league_response.status_code}")
    return league_json