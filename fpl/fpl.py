from typing import List

import requests
import streamlit as st

LEAGUE_ID = 70016
BASE_URL = "https://draft.premierleague.com/api/"
GAME_URL = BASE_URL + "game"
LEAGUE_URL = BASE_URL + f"league/{LEAGUE_ID}/details"
BOOTSTRAP_URL = BASE_URL + "bootstrap-static"

class LivePlayerData:
    def __init__(self, id, points, goals, assists, minutes):
        self.id = id
        self.points = points
        self.goals = goals
        self.assists = assists
        self.minutes = minutes
        
    def __repr__(self):
        return f"LivePlayerData(id={self.id}, points={self.points}, goals={self.goals}, assists={self.assists}, minutes={self.minutes})"

class Player:
    def __init__(self, id, club_id, name):
        self.id = id
        self.club_id = club_id
        self.name = name

    def __repr__(self):
        return f"Player(id={self.id}, name='{self.name}', club_id='{self.club_id}')"

class FplTeam:
    def __init__(self, id, entry_id, manager_name, team_name, players=None):
        self.id = id
        self.entry_id = entry_id
        self.manager_name = manager_name
        self.team_name = team_name
        self.players = players if players is not None else []

    def __repr__(self):
        return f"FplTeam(id={self.id}, entry_id={self.entry_id}, manager_name='{self.manager_name}', team_name='{self.team_name}', players={self.players})"

class Club:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return f"Club(id={self.id}, name='{self.name}')"

class FplMatchup:
    def __init__(self, team_1_id, team_1_points, team_2_id, team_2_points):
        self.fpl_team_id_1 = team_1_id
        self.fpl_team_id_2 = team_2_id
        self.team_1_points = team_1_points
        self.team_2_points = team_2_points

    def __repr__(self):
        return f"FplMatchup(fpl_team_id_1={self.fpl_team_id_1}, fpl_team_id_2={self.fpl_team_id_2}, team_1_points={self.team_1_points}, team_2_points={self.team_2_points})"

def create_fpl_team_map(league_entries: List[dict]) -> dict[int, FplTeam]:
    """Create {id: FplTeam} from league entries data."""
    teams = {}
    for entry in league_entries:
        id = entry.get('id')
        entry_id = entry.get('entry_id')
        manager_name = entry.get('player_first_name')
        team_name = entry.get('entry_name')
        teams[id] = FplTeam(id, entry_id, manager_name, team_name)
    return teams

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

    all_clubs_map = {team.get('id'): Club(team.get('id'), team.get('name')) for team in bootstrap_json.get('teams', [])}
    all_players_map = {player.get('id'): Player(player.get('id'), player.get('team'), player.get('web_name')) for player in bootstrap_json.get('elements', [])}

    live_json = get_live_data()
    live_players = live_json.get('elements', [])
    live_player_data = {int(i): LivePlayerData(i,
                                                         live_players[i].get('stats', {}).get('total_points', 0),
                                                         live_players[i].get('stats', {}).get('goals_scored', 0),
                                                         live_players[i].get('stats', {}).get('assists', 0),
                                                         live_players[i].get('stats', {}).get('minutes', 0)) for i in live_players}
    league_json = get_league_details()
    league_teams = league_json.get('league_entries', [])
    fpl_team_map = create_fpl_team_map(league_teams) # map of id -> FplTeam
    
    # Fetch players for each team
    for _, team in fpl_team_map.items():
        players = get_team_players(team.entry_id, current_gameweek, all_players_map)
        team.players = players

    matches = league_json.get('matches', [])
    fpl_matchups = []
    for match in matches:
        if match.get('event') == current_gameweek:
            fpl_matchups.append(FplMatchup(match.get('league_entry_1'), match.get('league_entry_1_points'), match.get('league_entry_2'), match.get('league_entry_2_points')))


    for matchup in fpl_matchups:
        fpl_team_1 = fpl_team_map.get(int(matchup.fpl_team_id_1))
        fpl_team_2 = fpl_team_map.get(int(matchup.fpl_team_id_2))
        team1_xi = []
        team2_xi = []
        for player in fpl_team_1.players:
            live_data = live_player_data.get(player.id)
            if live_data:
                team1_xi.append(f"{player.name} ({all_clubs_map[player.club_id].name}) - {live_data.points} pts, {live_data.goals} goals, {live_data.assists} assists, {live_data.minutes} mins")
        for player in fpl_team_2.players:
            live_data = live_player_data.get(player.id)
            if live_data:
                team2_xi.append(f"{player.name} ({all_clubs_map[player.club_id].name}) - {live_data.points} pts, {live_data.goals} goals, {live_data.assists} assists, {live_data.minutes} mins")
        print(f"{fpl_team_1.manager_name} ({fpl_team_1.team_name}) vs {fpl_team_2.manager_name} ({fpl_team_2.team_name})")
        st.subheader(f"{fpl_team_1.team_name} vs {fpl_team_2.team_name}")
        st.subheader(f"({fpl_team_1.manager_name} vs {fpl_team_2.manager_name})")
        st.subheader(f"Score: " + f"{matchup.team_1_points} - {matchup.team_2_points}")
        data = {fpl_team_1.team_name: team1_xi, fpl_team_2.team_name: team2_xi}
        st.dataframe(data, height=422)


if __name__ == "__main__":
    main()