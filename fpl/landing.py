from typing import List

import random
import requests
import streamlit as st

from classes import FplTeam
from http_helpers import get_current_gameweek, get_league_json

LEAGUE_ID = 70016
BASE_URL = "https://draft.premierleague.com/api/"
GAME_URL = BASE_URL + "game"
LEAGUE_URL = BASE_URL + f"league/{LEAGUE_ID}/details"
BOOTSTRAP_URL = BASE_URL + "bootstrap-static"

def get_bootstrap_json():
    bootstrap_response = requests.get(BOOTSTRAP_URL)
    if bootstrap_response.status_code == 200:
        bootstrap_json = bootstrap_response.json()
    else:
        raise Exception(f"Failed to fetch bootstrap data: {bootstrap_response.status_code}")
    return bootstrap_json

def create_fpl_team_map(league_entries: List[dict]) -> dict[int, FplTeam]:
    """Create {id: FplTeam} from league entries data."""
    teams = {}
    for entry in league_entries:
        id = entry.get('id')
        entry_id = entry.get('entry_id')
        manager_name = entry.get('player_first_name')
        if manager_name == "James":
            manager_name = "Jimmy"
        team_name = entry.get('entry_name')
        teams[id] = FplTeam(id, entry_id, manager_name, team_name)
    return teams

def main():
    emojis = [
        ":joy:", ":rofl:", ":sweat_smile:", ":upside_down_face:", ":wink:", ":grin:", ":laughing:",
        ":stuck_out_tongue_winking_eye:", ":stuck_out_tongue_closed_eyes:", ":stuck_out_tongue:",
        ":kissing:", ":kissing_smiling_eyes:", ":kissing_closed_eyes:",
        ":open_mouth:", ":grimacing:", ":hushed:", ":smirk:", ":roll_eyes:",
        ":astonished:", ":anguished:", ":angry:", ":rage:", ":triumph:", ":scream:", ":tired_face:", ":weary:",
        ":sob:", ":cry:", ":cold_sweat:", ":persevere:", ":sweat:", ":dizzy_face:", ":clown_face:", ":alien:", ":robot:",
        ":ghost:", ":skull:", ":skull_and_crossbones:", ":japanese_ogre:", ":japanese_goblin:", ":smiling_imp:", ":imp:", ":space_invader:",
        ":see_no_evil:", ":hear_no_evil:", ":speak_no_evil:",
        ":smiley_cat:", ":smile_cat:", ":joy_cat:", ":heart_eyes_cat:", ":smirk_cat:", ":kissing_cat:", ":scream_cat:", ":crying_cat_face:", ":pouting_cat:",
        ":monkey:", ":monkey_face:", ":penguin:", ":turtle:", ":octopus:", ":blowfish:", ":dolphin:", ":unicorn:", ":camel:", ":dromedary_camel:", ":dragon:", ":dragon_face:",
        ":jack_o_lantern:", ":santa:", ":tada:", ":confetti_ball:", ":balloon:", ":video_game:", ":game_die:", ":dart:", ":trophy:", ":trumpet:", ":saxophone:", ":tophat:", ":crown:", ":womans_hat:", ":eyeglasses:", ":crystal_ball:", ":sparkles:", ":star2:", ":zap:", ":boom:",
        ":dizzy:", ":sweat_drops:", ":dash:", ":100:", ":ok_hand:", ":+1:", ":-1:", ":clap:", ":metal:", ":poop:"
    ]
    current_gameweek = get_current_gameweek()
    st.header(f"Current gameweek: {current_gameweek}", divider="gray")
    bootstrap_json = get_bootstrap_json()
    league_json = get_league_json()
    league_teams = league_json.get('league_entries', [])
    fpl_team_map = create_fpl_team_map(league_teams) # map of id -> FplTeam
    team_name_to_id_map = {team.team_name + ' ' + random.choice(emojis): team.id for _, team in fpl_team_map.items()}
    st.session_state.bootstrap_json = bootstrap_json
    st.title("Welcome to :soccer: :blue[Relegation Royale] :fire:")
    st.write("First off...choose your squad:")
    cols = st.columns(1)
    button_labels = list(team_name_to_id_map.keys())

    st.set_page_config(page_title="Relegation Royale", page_icon=":soccer:", layout="wide")
    for i, col in enumerate(cols * 8):  # 8 buttons, 4 per row
        if col.button(button_labels[i], key=f"btn_{i}", width="content"):
            st.session_state.current_team = i
            # st.switch_page("details.py")  # Navigate to the details page

if __name__ == "__main__":
    main()