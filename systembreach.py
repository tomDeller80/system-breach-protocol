from core import PhysicsEngine
from scoreboard import Scoreboard
from interface import Interface
from mixer import AudioManager
from players import Players
from levels import Levels
from sections import *
from sprites import *
from popups import *

class SystemBreach:

    def __init__(self):
        # Boot the runtime and construct the shared game services.
        pg.init()

        # The game starts at the menu and transitions into play from there.
        self.state = 'ready'
        self.running = True

        # Window chrome and mouse setup.
        pg.display.set_caption("System Breach: Protocol")

        # Mouse
        pg.mouse.set_visible(True)
        pg.mouse.set_pos(640, 600)

        # Display surface and timing clock.
        self.size = width, height = 1280, 720
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()

        # Load the window icon from the packaged assets.
        icon_image, _ = Storage.load_image("assets/ico/ico.png")
        pg.display.set_icon(icon_image)
        pg.display.set_caption("System Breach: Protocol")

        # Keep gameplay constrained to the visible playfield.
        self.active_area = pg.Rect(15, 60, 1115, 650)

        # Core services that other modules read from.
        self.scoreboard = Scoreboard()
        self.audio_manager = AudioManager()
        self.levels = Levels()

        # Active powerup inventory for the current player.
        self.powerups = []

        # Primary player sprites.
        self.paddle = Paddle(self)
        self.ball = Ball(self, self.paddle)

        # Sprite groups for collision and update management.
        self.balls = pg.sprite.Group()
        self.bricks = pg.sprite.Group()
        self.modules = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.debris = pg.sprite.Group()

        # RenderPlain keeps draw order simple for the main playfield.
        self.all_sprites = pg.sprite.RenderPlain(self.paddle, self.ball)

        # Shared physics and HUD rendering.
        self.physics = PhysicsEngine()
        self.interface = Interface(self)

        # Persisted player profiles.
        self.players = Players()

        # Modal overlays used by the login and pause flow.
        self.popups = {
            "new_player": Login(self, self.active_area),
            "pause": Pause(self, self.active_area),
            "quit_confirm": QuitConfirm(self, self.active_area),
            "no_more_levels": NoMoreLevels(self, self.active_area),
            "completed": Completed(self, self.active_area)
        }

        # Section controller map for menu, play, game over, and scoreboard views.
        self.sections = {
            "menu": MainMenuSection(self),
            "play": GameSection(self),
            "game-over": GameOverSection(self),
            "score": ScoreMenuSection(self)
        }

        self.active_section = self.sections['menu']

    def request_quit(self):
        # Defer pygame shutdown until the main loop has stopped drawing.
        self.running = False

    def run(self):
        # Main game loop: process input, update state, then render the active section.
        while self.running:

            self.clock.tick(60)

            # Handle Events
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.request_quit()

            if not self.running:
                break

            # Section-Specific
            self.active_section.handle_events(events)

            if not self.running:
                break

            self.active_section.update()

            if not self.running:
                break

            self.active_section.draw()

            pg.display.flip()

    def reset_game(self):
        # Clear run state while keeping the loaded assets and menus alive.
        self.levels.reset() # Reset level 1
        self.scoreboard.reset()  # Reset lives to 3 and score to 0
        self.interface.update_score(self.scoreboard.get_formatted_score()) # Reset UI

        # Remove all dynamic gameplay objects before starting over.
        self.balls.empty()   # Remove all active balls
        self.bricks.empty()  # Remove all old brick sprites
        self.modules.empty()  # Remove any active modules/powerups
        self.explosions.empty()  # Clear any lingering visual effects
        self.debris.empty() # Clear any debris flying around
        self.powerups[:] = []

        # Rebuild the first level from scratch.
        self.sections['play'].spawn_blocks()

        # Re-center the paddle and ball.
        self.paddle.reset()
        self.ball.reset()

        # Clear the selected profile so the login flow can pick a new one.
        self.players.reset_player()

        # Re-enter the play section with the starting level loaded.
        self.sections['play'].start_new_level()

    def switch_section(self, section_key):
        # Swap the active screen controller and adjust mouse capture appropriately.
        try:

            self.active_section = self.sections[section_key]

            if section_key == 'play':
                self.audio_manager.play_music('synthwav')
                pg.mouse.set_pos(self.size[0] // 2, self.size[1] // 2)
                if self.state == 'ready':  # Ensure state moves to playing
                    self.state = 'playing'
            else:
                pg.mouse.set_visible(True)
                pg.event.set_grab(False)
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
                self.state = 'ready'

        except KeyError as e:
            print(f"Section error: {e}")


    def update_score(self, credits):
        # Keep the data model and HUD text in sync after scoring.
        self.scoreboard.update(credits)
        self.interface.update_score(self.scoreboard.get_formatted_score())

    def add_life(self):
        # Cap lives at three so the UI stays consistent.
        if self.scoreboard.lives < 3:
            self.scoreboard.gain_life()

    def lose_life(self):
        # Delegate death handling to the scoreboard and game-over flow.
        self.scoreboard.lose_life()

        # check if any lives left
        if self.scoreboard.lives <= 0:
           self.trigger_game_over()


    def trigger_game_over(self):
        # Fade out the current run and transition to the game-over section.
        self.state = 'ready'

        # Fadeout music and play purge effect
        pg.mixer.music.fadeout(500)
        self.audio_manager.play_sfx('purge')

        # Change state
        self.switch_section('game-over')

        # Reset game
        self.reset_game()
