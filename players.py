from core import Storage
from datetime import datetime

class Player():

    def __init__(self, name, level, lives, score, power_ups=None, created_at=None, last_played=None):
        # Player objects are lightweight records used for save data and the login list.
        self.name = name
        self.level  = level
        self.lives = lives
        self.score = score
        self.power_ups = power_ups or []
        self.created_at = created_at or datetime.now().isoformat()
        self.last_played = last_played or self.created_at


class Players():

    def __init__(self):
        # Keep the full roster in memory and mirror it to the app data file.
        self.players = []
        self.load_players()
        self.current_player = None


    def add_player(self, profile):
        # Build a new persistent player profile from the login form payload.
        player = Player(
                profile["name"],
                profile["level"],
                profile["lives"],
                profile["score"],
            )

        self.players.append(
            player
        )

        self.save_players()

        return player


    def set_player(self, name):
        # Select the named profile and refresh its last-played timestamp.
        for player in self.players:
            if player.name == name:
                self.current_player = player

        self.update_player()

    def get_player(self):
        return self.current_player


    def reset_player(self):
        # Clear the active selection without deleting saved profiles.
        self.current_player = None


    def update_player(
            self, player = None,
            level = None,
            lives = None,
            score = None,
            power_ups = None,
            created_at = None,
            last_played = None
    ):
        # Update only the fields that were explicitly supplied.
        updated_player = player or self.current_player

        if not updated_player:
            return

        if level is not None:
            updated_player.level = level
        if lives is not None:
            updated_player.lives = lives
        if score is not None:
            updated_player.score = score
        if power_ups is not None:
            updated_player.power_ups = power_ups

        if created_at is not None:
            updated_player.created_at = created_at

        updated_player.last_played = last_played if last_played is not None else datetime.now().isoformat()

        self.save_players() # Save Players


    def load_players(self):
        # Load persisted player data or fall back to the built-in starter roster.
        try:
            existing_players = Storage.read_json(json_file="players.json", is_static=False)
        except FileNotFoundError:

            existing_players = {
                                 "players" : { }
                               }

            #existing_players = {
            #    "players" : {
            #        "1" : {"name": "NEO_PHYTE3", "level": "Data Stream Core", "lives": 3, "score": 56786, "power_ups":[], "created_at": None, "last_played": None},
            #        "2" : {"name": "GHOST_404", "level": "Sub-Net Proxy", "lives": 1, "score": 76769, "power_ups":[], "created_at": None, "last_played": None},
            #        "3" : {"name": "CYPHER_K", "level": "Firewall Perimeter", "lives": 2, "score": 11234, "power_ups":[], "created_at": None, "last_played": None},
            #        "4" : {"name": "OVERRIDE_X", "level": "Root Access Mainframe", "lives": 3, "score": 67565, "power_ups":[], "created_at": None, "last_played": None},
            #        "5" : {"name": "ANON_USER", "level": "Sector 0-7 Entry", "lives": 1, "score": 12324, "power_ups":[], "created_at": None, "last_played": None}
            #    }
            #}

        for i in range(len(existing_players["players"])):
            player = existing_players["players"][f"{i + 1}"]
            self.players.append(
                Player(player["name"],
                       player["level"],
                       player["lives"],
                       player["score"],
                       player.get("power_ups"),
                       player.get("created_at"),
                       player.get("last_played")
                       )
            )
            self.players.sort(key=lambda player: player.last_played, reverse=True)

    def auto_select_most_recent(self):
        # Restore the most recently used profile for the game-over resume flow.
        if not self.players:
            self.current_player = None
            return None

        return max(self.players, key=lambda p: p.last_played)


    def save_players(self):
        # Serialize the in-memory roster back into the app data file.
        players = { "players" : {}}

        for i, player in enumerate(self.players):

            players["players"][f"{i+1}"] = {
                "name":player.name,
                "level":player.level,
                "lives":player.lives,
                "score":player.score,
                "power_ups":player.power_ups,
                "created_at": player.created_at,
                "last_played":player.last_played
            }

        Storage.write_json(json_file="players.json", data=players)
