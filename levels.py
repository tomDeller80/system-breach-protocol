from core import Storage

# Level metadata and progression data are loaded from JSON and exposed through a simple index.

class Level:
    def __init__(self, number, title, layout):
        # Keep the level definition as plain data so the game can swap layouts without extra logic.
        self.number = number
        self.title = title
        self.layout = layout

class Levels:

    def __init__(self):
        # The active level is tracked by index so the game can advance and reset quickly.
        self.levels = []
        self.index = 0

        self.load_levels()

    def load_levels(self):
        # Pull the baked level list from disk and convert each entry into a Level object.
        data = Storage().read_json("data/levels.json", True)
        levels = data["levels"]

        for id, level in levels.items():
            self.levels.append(Level(int(id), level['title'], level['modules']))

    def get_level(self):
        # The current index points at the active stage.
        return self.levels[self.index]

    def set_level(self, level_title):
        # Restore a level by title when loading a previous player session.
        for i, level in enumerate(self.levels):
            if level.title == level_title:
                self.index = i


    def next_level(self):
        # Advance to the next level in the list.
        self.index += 1
        return self.levels[self.index]

    def reset(self):
        # Reset progression back to the first level.
        self.index = 0
