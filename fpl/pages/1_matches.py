from typing import List

import pandas as pd
import streamlit as st

from classes import Club, ElementType, Fixture, FplMatchup, FplTeam, LivePlayerData, Player

from http_helpers import get_bootstrap_json, get_current_gameweek, get_league_json, get_live_data, get_team_players
from utils import create_fpl_team_map

def render_team_table(team_xi: List[Player], element_types_map, live_player_data_map, live_fixtures, all_clubs_map):
    columns = ["Player", "Points", "Goals", "Assists", "Minutes", "Game"]
    data = []
    for player in team_xi:
        live_player_data = live_player_data_map.get(player.id)
        if not live_player_data:
            data.append([])
            continue
        name_cell = player.name + f" ({element_types_map[player.element_type].position_name})"
        points_cell = live_player_data.points
        goals_cell = live_player_data.goals
        assists_cell = live_player_data.assists
        minutes_cell = live_player_data.minutes
        game_status_cell = ''
        for fixture in live_fixtures:
            if not (fixture.home_team == player.club_id or fixture.away_team == player.club_id):
                continue
            first_part = all_clubs_map[player.club_id].name + " vs. "
            second_part = all_clubs_map[fixture.away_team].name if fixture.home_team == player.club_id else all_clubs_map[fixture.home_team].name
            game_status_cell = first_part + second_part
            if not fixture.started:
                game_status_cell += ' - Upcoming'
            elif fixture.finished:
                game_status_cell += ' - Finished'
            else:
                game_status_cell += ' - On now!!'
            break
        data.append([name_cell, points_cell, goals_cell, assists_cell, minutes_cell, game_status_cell])
    df = pd.DataFrame(data, columns=columns)
    st.dataframe(df, hide_index=True)

def main():
    current_gameweek = get_current_gameweek()
    bootstrap_json = get_bootstrap_json()
    element_types_map = {pos.get('id'): ElementType(pos.get('id'), pos.get('singular_name_short')) for pos in bootstrap_json.get('element_types', [])}
    all_clubs_map = {team.get('id'): Club(team.get('id'), team.get('name')) for team in bootstrap_json.get('teams', [])}
    all_players_map = {player.get('id'): Player(player.get('id'), player.get('team'), player.get('web_name'), player.get('element_type')) for player in bootstrap_json.get('elements', [])}

    live_json = get_live_data(current_gameweek)
    live_fixtures_json = live_json.get('fixtures', [])
    live_players = live_json.get('elements', [])
    live_fixtures = [
        Fixture(
            home_team=fixture.get('team_h'),
            away_team=fixture.get('team_a'),
            home_score=fixture.get('team_h_score'),
            away_score=fixture.get('team_a_score'),
            started=fixture.get('started'),
            finished=fixture.get('finished')
        ) for fixture in live_fixtures_json]
    live_player_data_map = {int(i): LivePlayerData(i,
                                                         live_players[i].get('stats', {}).get('total_points', 0),
                                                         live_players[i].get('stats', {}).get('goals_scored', 0),
                                                         live_players[i].get('stats', {}).get('assists', 0),
                                                         live_players[i].get('stats', {}).get('minutes', 0)) for i in live_players}
    league_json = get_league_json()
    league_teams = league_json.get('league_entries', [])
    fpl_team_map = create_fpl_team_map(league_teams) # map of id -> FplTeam
    
    # Fetch players for each team
    for _, team in fpl_team_map.items():
        team.players = get_team_players(team.entry_id, current_gameweek, all_players_map)

    matches = league_json.get('matches', [])
    fpl_matchups = []
    for match in matches:
        if match.get('event') == current_gameweek:
            fpl_matchups.append(FplMatchup(match.get('league_entry_1'), match.get('league_entry_1_points'), match.get('league_entry_2'), match.get('league_entry_2_points')))

    for matchup in fpl_matchups:
        fpl_team_1 = fpl_team_map.get(int(matchup.fpl_team_id_1))
        fpl_team_2 = fpl_team_map.get(int(matchup.fpl_team_id_2))
        team1_xi = sorted(fpl_team_1.players[:11], key=lambda p: p.element_type, reverse=True)
        team2_xi = sorted(fpl_team_2.players[:11], key=lambda p: p.element_type, reverse=True)
        st.header(f"{fpl_team_1.team_name} ({fpl_team_1.manager_name}) vs {fpl_team_2.team_name} ({fpl_team_2.manager_name})")
        st.subheader(f"Score: " + f"{matchup.team_1_points} - {matchup.team_2_points}")
        st.write("**" + fpl_team_1.team_name + "**")
        render_team_table(team1_xi, element_types_map, live_player_data_map, live_fixtures, all_clubs_map)
        st.write("**" + fpl_team_2.team_name + "**")
        render_team_table(team2_xi, element_types_map, live_player_data_map, live_fixtures, all_clubs_map)
    
if __name__ == "__main__":
    main()