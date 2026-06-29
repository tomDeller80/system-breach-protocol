# Central score and life state for the current run.
class Scoreboard:
    def __init__(self):
        # Start every run with zero score and three lives.
        self.score = 0
        self.lives = 3

        # Block values are kept here so collision logic can stay in one place.
        self.points = {
            'purple': 100, 'light_purple': 100,
            'green': 100, 'light_green': 100,
            'blue': 100, 'light_blue': 100,
            'red': 100, 'orange': 100,
            'gold': 100,
            'powerup': 500,
            'hardened': 350,
            'volatile': 50
        }

    def update(self, credits):
        # Add points from the latest hit or pickup.
        self.score += int(credits)

    def reset(self):
        # Clear the run state without touching any persistence layer.
        self.score = 0
        self.lives = 3

    def lose_life(self):
        # Called when the primary ball is lost.
        self.lives -= 1

    def gain_life(self):
        # Called by the health powerup.
        self.lives += 1

    def set_lives(self, lives):
        # Restore a saved player state.
        self.lives = lives

    def get_lives(self):
        return self.lives

    def set_score(self, score):
        # Restore a saved player score.
        self.score = score

    def get_score(self):
        return self.score

    def get_formatted_score(self):
        # Keep the HUD width stable by zero-padding the displayed score.
        return f"{self.score:07}"

