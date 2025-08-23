import streamlit as st

from classes import Club, FplMatchup, FplTeam, LivePlayerData, Player

from http_helpers import get_bootstrap_json, get_current_gameweek, get_league_json, get_live_data, get_team_players
from utils import create_fpl_team_map

def main():
    current_gameweek = get_current_gameweek()
    bootstrap_json = get_bootstrap_json()
    all_clubs_map = {team.get('id'): Club(team.get('id'), team.get('name')) for team in bootstrap_json.get('teams', [])}
    all_players_map = {player.get('id'): Player(player.get('id'), player.get('team'), player.get('web_name')) for player in bootstrap_json.get('elements', [])}

    live_json = get_live_data(current_gameweek)
    live_players = live_json.get('elements', [])
    live_player_data = {int(i): LivePlayerData(i,
                                                         live_players[i].get('stats', {}).get('total_points', 0),
                                                         live_players[i].get('stats', {}).get('goals_scored', 0),
                                                         live_players[i].get('stats', {}).get('assists', 0),
                                                         live_players[i].get('stats', {}).get('minutes', 0)) for i in live_players}
    league_json = get_league_json()
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