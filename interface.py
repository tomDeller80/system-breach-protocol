from core import Storage
import pygame as pg

class Interface:

    def __init__(self, game):
        # Own all HUD art, fonts, and reusable layout surfaces for the active run.
        self.game = game
        self.screen = pg.display.get_surface()

        # Asset Loading
        self._load_fonts()
        self._load_assets()
        self._load_backgrounds()

        # Powerup Timers
        self.powerup_flash_timers = [0, 0, 0]


    def _load_fonts(self):
        # Load the shared typefaces used across HUD, menus, and score screens.
        self.score_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.level_number_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.level_title_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.life_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.rank_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.codename_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)

        # Keep the HUD palette consistent across the game.
        self.primary_neon = (0, 243, 255) #00f3ff (Cyber Cyan)
        self.alert_red = (255, 0, 60) #ff003c (Glitch Red)
        self.level_purple = (188, 0, 255) #bc00ff (Neon Purple)
        self.status_yellow = (98, 88, 24) #fce13c (Yellow)


    def _load_assets(self):
        # Load icons and button art used by the HUD.
        self.life, _ = Storage.load_image("assets/sprites/life.png")

        # Module (multi, speed, health, buffer)
        self.multi, _ = Storage.load_image("assets/sprites/multi.png")
        self.speed, _ = Storage.load_image("assets/sprites/speed.png")
        self.health, _ = Storage.load_image("assets/sprites/health.png")
        self.buffer, _ = Storage.load_image("assets/sprites/buffer.png")

        # Key Hints (Key: 1,2,3)
        self.hint_1, _ = Storage.load_image(filename="assets/sprites/key_1.png", scale=1)
        self.hint_2, _ = Storage.load_image(filename="assets/sprites/key_2.png", scale=1)
        self.hint_3, _ = Storage.load_image(filename="assets/sprites/key_3.png", scale=1)

        # Cache the initial score text so the HUD can be drawn immediately.
        self.score = self.score_font.render(
            f"SCORE: {self.game.scoreboard.get_formatted_score()}", True, self.primary_neon)

        # Render the current level label once at load time.
        active_index = self.game.levels.index
        active_level = self.game.levels.levels[active_index]

        self.level = self.level_number_font.render(f"LEVEL: {active_level.number}", True, self.level_purple)
        self.title = self.level_title_font.render(f" - {active_level.title.upper()}", True, self.primary_neon)
        self.lives = self.level_number_font.render("LIVES:", True, self.primary_neon)


    def _load_backgrounds(self):
        # Backgrounds are pre-scaled to the current window size for cheap swaps later.
        size = self.screen.get_size()

        backgrounds = [
            Storage.load_image("assets/backgrounds/cyber.png")[0],
            Storage.load_image("assets/backgrounds/industrial.png")[0],
            Storage.load_image("assets/backgrounds/quantum.png")[0],
            Storage.load_image("assets/backgrounds/critical.png")[0],  # Fixed duplicate asset path from copy-paste
            Storage.load_image("assets/backgrounds/alert.png")[0]
        ]

        self.backgrounds = [pg.transform.scale(bg, size) for bg in backgrounds]

        self.game_background = self.backgrounds[0]


        self.menu_background, _ = Storage.load_image("assets/backgrounds/main.png")
        self.game_over_background, _ = Storage.load_image("assets/backgrounds/gameover.png")
        self.scoreboard_background, _ = Storage.load_image("assets/backgrounds/scoreboard.png")

        self.game_background = pg.transform.scale(self.game_background, size)
        self.menu_background = pg.transform.scale(self.menu_background, size)
        self.game_over_background = pg.transform.scale(self.game_over_background, size)
        self.scoreboard_background = pg.transform.scale(self.scoreboard_background, size)


    def draw_menu_layout(self):
        # Main menu backdrop.
        self.screen.blit(self.menu_background, (0, 0))

    def draw_game_over_layout(self):
        # Game-over backdrop.
        self.screen.blit(self.game_over_background, (0, 0))

    def draw_scoreboard_layout(self):
        # Scoreboard backdrop.
        self.screen.blit(self.scoreboard_background, (0, 0))


    def draw_score_results(self, results):
        # Render a ranked list of player names and scores onto the scoreboard screen.
        x = 225
        y = 250

        for num, player in enumerate(results):

            # Rank
            self.screen.blit(
                self.rank_font.render(f"{(num + 1)}", True, self.primary_neon),
                dest=(x, y + (50 * num))
            )

            # Codename
            self.screen.blit(
                self.codename_font.render(f"{player.name}", True, self.primary_neon),
                dest=((x + 125), y + (50 * num))
            )

            # Score
            self.screen.blit(
                self.codename_font.render(f"{player.score}", True, self.primary_neon),
                dest=((x + 700), y + (50 * num))
            )

    def draw_lives(self):
        # Show one life icon per remaining life.
        for index in range(self.game.scoreboard.lives):
            x = 1145 + (index * 37)
            self.screen.blit(self.life, dest=(x, 12))


    def draw_powerups(self):
        # Display up to three active powerups.
        now = pg.time.get_ticks()

        for index, powerup in enumerate(self.game.powerups[:3]):
            y = 130 + (index * 110)
            x = 1161

            if powerup:
                icon = getattr(self, powerup)
                self.screen.blit(icon, dest=(x, y))

                # Flash if access denied
                if now < self.powerup_flash_timers[index]:
                    flash_surf = pg.Surface(icon.get_size(), pg.SRCALPHA)
                    flash_surf.fill((255, 0, 60, 120))
                    self.screen.blit(flash_surf, (x, y), special_flags=pg.BLEND_RGBA_MULT)

                # Key hint overlays
                hint_x = x + 65
                hint_y = y + 60

                hint = getattr(self, f"hint_{index + 1}")
                self.screen.blit(hint, (hint_x, hint_y))



    def draw_game_hub(self):
        # Draw the in-game HUD band and overlay the current stat widgets.
        self.screen.blit(self.game_background, (0, 0))

        # Messaging
        self.screen.blit(self.score, dest=(60, 10))  # score
        self.screen.blit(self.level, dest=(400, 10))  # level name
        self.screen.blit(self.title, dest=(525, 10))  # level number
        self.screen.blit(self.lives, dest=(1045, 10))  # lives

        # Lives
        self.draw_lives()

        # powerups
        self.draw_powerups()


    # Update Level
    def update_level_details(self):
        # Refresh the level label when the active stage changes.
        active_index = self.game.levels.index
        active_level = self.game.levels.levels[active_index]
        self.level = self.level_number_font.render(f"LEVEL: {active_level.number}", True, self.level_purple)
        self.title = self.level_title_font.render(f" - {active_level.title.upper()}", True, self.primary_neon)

        if active_level.number < 10:
            bg_index = 0
        else:
            bg_index = max(0, active_level.number - 1) // 10
            bg_index = bg_index % len(self.backgrounds)

        self.game_background = self.backgrounds[bg_index]

    # Update Score
    def update_score(self, credits):
        # Re-render the score text whenever the score changes.
        self.score = self.score_font.render(
            f"SCORE: {credits}", True, self.primary_neon)

    # Access Denied: Powerup
    def trigger_powerup_fail(self, index, time = 500):
        # Flash the relevant powerup slot and play the denial sound.
        self.powerup_flash_timers[index] = pg.time.get_ticks() + time
        self.game.audio_manager.play_sfx('denied')
