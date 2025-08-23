import pandas as pd
import streamlit as st

from http_helpers import get_league_json
from utils import create_fpl_team_map

def main():
    st.title("Relegation Royale: Standings")
    league_json = get_league_json()
    standings_json = league_json.get('standings', [])
    league_teams = league_json.get('league_entries', [])
    fpl_team_map = create_fpl_team_map(league_teams) # map of id -> FplTeam
    if not standings_json:
        st.error("No standings data available.")
        return
    columns = ["Rank", "Team", "W", "D", "L", "Points", "Score +", "Score +/-"]
    data = []
    for standing in standings_json:
        rank = standing.get('rank')
        fpl_team = fpl_team_map[standing.get('league_entry')]
        wins = standing.get('matches_won', 0)
        draws = standing.get('matches_drawn', 0)
        losses = standing.get('matches_lost', 0)
        points = standing.get('total', 0)
        score_for = standing.get('points_for', 0)
        score_diff = score_for - standing.get('points_against', 0)
        data.append([
            rank,
            fpl_team.team_name,
            wins,
            draws,
            losses,
            points,
            score_for,
            score_diff
        ])
    df = pd.DataFrame(data, columns=columns)
    st.dataframe(df, hide_index=True)
    st.write("Note: This table only updates at the conclusion of each gameweek, of course")
    st.write("See the **matches** page for live data")

if __name__ == "__main__":
    main()