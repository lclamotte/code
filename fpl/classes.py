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