from typing import List
import requests

LEAGUE_ID = 70016
BASE_URL = "https://draft.premierleague.com/api/"
LEAGUE_URL = BASE_URL + f"league/{LEAGUE_ID}/details"

class Team:
    def __init__(self, id, manager_name, team_name):
        self.id = id
        self.manager_name = manager_name
        self.team_name = team_name

    def __repr__(self):
        return f"Team(id={self.id}, manager_name='{self.manager_name}', team_name='{self.team_name}')"

def main():
    response = requests.get(LEAGUE_URL)
    if response.status_code == 200:
        json_data = response.json()
        print(json_data)
    else:
        raise Exception(f"Failed to fetch league details: {response.status_code}")

    league_entries = json_data.get('league_entries', [])
    teams = []
    for entry in league_entries:
        id = entry.get('entry_id')
        manager_name = entry.get('player_first_name')
        team_name = entry.get('entry_name')
        teams.append(Team(id, manager_name, team_name))
    for team in teams:
        print(team)

if __name__ == "__main__":
    main()