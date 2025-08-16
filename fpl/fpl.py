from typing import List
import requests

LEAGUE_ID = 70016
BASE_URL = "https://draft.premierleague.com/api/"
GAME_URL = BASE_URL + "game"
LEAGUE_URL = BASE_URL + f"league/{LEAGUE_ID}/details"

class FplTeam:
    def __init__(self, id, manager_name, team_name):
        self.id = id
        self.manager_name = manager_name
        self.team_name = team_name

    def __repr__(self):
        return f"FplTeam(id={self.id}, manager_name='{self.manager_name}', team_name='{self.team_name}')"

class PremierLeagueTeam:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return f"PremierLeagueTeam(id={self.id}, name='{self.name}')"

class FplMatchup:
    def __init__(self, fpl_team_id_1, fpl_team_id_2):
        self.fpl_team_id_1 = fpl_team_id_1
        self.fpl_team_id_2 = fpl_team_id_2

    def __repr__(self):
        return f"FplMatchup(fpl_team_id_1={self.fpl_team_id_1}, fpl_team_id_2={self.fpl_team_id_2})"

def create_fpl_team_map(league_entries: List[dict]) -> dict[int, FplTeam]:
    """Create {id: FplTeam} from league entries data."""
    teams = {}
    for entry in league_entries:
        id = entry.get('id')
        manager_name = entry.get('player_first_name')
        team_name = entry.get('entry_name')
        teams[id] = FplTeam(id, manager_name, team_name)
    return teams

def get_league_details():
    league_response = requests.get(LEAGUE_URL)
    if league_response.status_code == 200:
        league_json = league_response.json()
    else:
        raise Exception(f"Failed to fetch league details: {league_response.status_code}")
    return league_json

def get_current_gameweek():
    game_response = requests.get(GAME_URL)
    if game_response.status_code == 200:
        game_json = game_response.json()
    else:
        raise Exception(f"Failed to fetch current gameweek: {game_response.status_code}")
    return game_json.get('current_event')

def main():
    current_gameweek = get_current_gameweek()
    print(f"Current gameweek: {current_gameweek}")

    league_json = get_league_details()
    league_teams = league_json.get('league_entries', [])
    fpl_team_map = create_fpl_team_map(league_teams)
    for id in fpl_team_map:
        print(fpl_team_map[id])

    matches = league_json.get('matches', [])
    fpl_matchups = []
    for match in matches:
        if match.get('event') == current_gameweek:
            fpl_matchups.append(FplMatchup(match.get('league_entry_1'), match.get('league_entry_2')))

    for matchup in fpl_matchups:
        fpl_team_1 = fpl_team_map.get(int(matchup.fpl_team_id_1))
        fpl_team_2 = fpl_team_map.get(int(matchup.fpl_team_id_2))
        print(f"{fpl_team_1.manager_name} ({fpl_team_1.team_name}) vs {fpl_team_2.manager_name} ({fpl_team_2.team_name})")

if __name__ == "__main__":
    main()