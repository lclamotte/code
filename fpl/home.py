from typing import List

import requests
import streamlit as st
from classes import LivePlayerData, FplTeam, Player, Club, FplMatchup

LEAGUE_ID = 70016
BASE_URL = "https://draft.premierleague.com/api/"
GAME_URL = BASE_URL + "game"
LEAGUE_URL = BASE_URL + f"league/{LEAGUE_ID}/details"
BOOTSTRAP_URL = BASE_URL + "bootstrap-static"

def get_team_players(team_id: int, gameweek: int, all_players_map) -> List[Player]:
    """Fetch players for a specific team in a specific gameweek."""
    team_url = f"{BASE_URL}entry/{team_id}/event/{gameweek}"
    response = requests.get(team_url)
    
    if response.status_code == 200:
        team_data = response.json()
        picks = team_data.get('picks', [])
        players = []
        
        for pick in picks:
            player_id = pick.get('element')
            if player_id is not None:
                player_info = all_players_map[player_id]
                players.append(Player(player_id, player_info.club_id, player_info.name))
        
        return players
    else:
        print(f"Failed to fetch team {team_id} data: {response.status_code}")
        return []

def get_live_data():
    live_response = requests.get(f"{BASE_URL}event/1/live")
    if live_response.status_code == 200:
        live_json = live_response.json()
    else:
        raise Exception(f"Failed to fetch live data: {live_response.status_code}")
    return live_json

def get_current_gameweek():
    game_response = requests.get(GAME_URL)
    if game_response.status_code == 200:
        game_json = game_response.json()
    else:
        raise Exception(f"Failed to fetch current gameweek: {game_response.status_code}")
    return game_json.get('current_event')

def get_bootstrap_data():
    bootstrap_response = requests.get(BOOTSTRAP_URL)
    if bootstrap_response.status_code == 200:
        bootstrap_json = bootstrap_response.json()
    else:
        raise Exception(f"Failed to fetch bootstrap data: {bootstrap_response.status_code}")
    return bootstrap_json

def main():
    st.title("Welcome to :blue[Relegation Royale] :soccer:")
    bootstrap_json = get_bootstrap_data()
    current_gameweek = get_current_gameweek()
    st.header(f"Current gameweek: {current_gameweek}", divider="gray")


if __name__ == "__main__":
    main()