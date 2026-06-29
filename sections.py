from buttons import Button
from interface import Interface
from sprites import *
import pygame as pg
import random


class Section:

    def __init__(self, game):
        # Base class that gives every screen access to the shared game instance.
        self.game = game

    def handle_events(self, events):
        for event in events:
            pass

    def update(self): pass

    def draw(self):  pass

class MainMenuSection(Section):

    def __init__(self, game):
        super().__init__(game)

        # Start the menu with the standard crosshair cursor and load its buttons.
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)

        self._load_assets()

    def _load_assets(self):
        # Center the menu controls around the middle of the screen.
        self.active_area = self.game.active_area
        area_center = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)

        self.start_btn = Button(
            game=self.game,
            assets=['start.png', 'start_hover.png'],
            pos=(area_center[0], (area_center[1] + 125)),
            callback=self.start_game
        )

        self.leaderboard_btn = Button(
            game=self.game,
            assets=['board.png', 'board_hover.png'],
            pos=(area_center[0], (area_center[1] + 200)),
            callback=self.view_leaderboard
        )

        self.exit_btn = Button(
            game=self.game,
            assets=['exit.png', 'exit_hover.png'],
            pos=(area_center[0], (area_center[1] + 275)),
            callback=self.exit_game
        )

    def start_game(self):
        # Enter the play section and show the login overlay for profile selection.
        self.game.switch_section("play")
        self.game.state = "login"
        self.game.popups['new_player'].show()


    def view_leaderboard(self):
        # Open the scoreboard section from the menu.
        self.game.switch_section("score")


    def exit_game(self):
        # Ask the outer loop to stop before pygame tears down the display.
        self.game.request_quit()

    def handle_events(self, events):

        for event in events:

            self.start_btn.handle_event(event)
            self.leaderboard_btn.handle_event(event)
            self.exit_btn.handle_event(event)


    def draw(self):

        self.game.interface.draw_menu_layout()

        self.start_btn.draw()
        self.leaderboard_btn.draw()
        self.exit_btn.draw()

        pg.display.flip()

class ScoreMenuSection(Section):

    def __init__(self, game):
        super().__init__(game)
        # Cache the top scores for rendering on the leaderboard screen.
        self.top_scores = []
        self._load_data()

    def _load_data(self):
        # Sort by score first, then most recent play time as a tiebreaker.
        self.top_scores = sorted(
            self.game.players.players,
            key = lambda p: (p.score, p.last_played),
            reverse=True
        )[:6]

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                # Any click returns the user to the main menu.
                self.game.switch_section("menu")

    def draw(self):
        # Refresh the list each frame so newly created players appear immediately.
        self._load_data()

        # Draw the cached leaderboard results over the scoreboard background.
        self.game.interface.draw_scoreboard_layout()
        self.game.interface.draw_score_results(self.top_scores)
        pg.display.flip()


class GameSection(Section):

    def __init__(self, game):
        super().__init__(game)

        # Keep direct references to the active gameplay sprites and groups.
        self.paddle = game.paddle
        self.ball = game.ball
        self.balls = game.balls
        self.bricks = game.bricks
        self.modules = game.modules
        self.powerups = game.powerups
        self.explosions = game.explosions
        self.debris = game.debris
        self.all_sprites = game.all_sprites

        # Modal overlays used during play.
        self.login = self.game.popups['new_player']
        self.pause = self.game.popups['pause']
        self.quit_confirm = self.game.popups['quit_confirm']
        self.no_more_levels = self.game.popups['no_more_levels']
        self.completed = self.game.popups['completed']

        # Used to avoid re-advancing the level on the first load.
        self.first_load = True

        # Build the starting level immediately.
        self.start_new_level()

    def start_new_level(self):
        # Advance the campaign only after the opening level has been loaded once.
        if self.first_load:
            self.first_load = False
        else:
            # Save the current player state before moving forward.
            self.game.levels.next_level()

            self.game.players.update_player(
                level=self.game.levels.get_level().title,
                score=self.game.scoreboard.get_score(),
                lives=self.game.scoreboard.get_lives(),
                power_ups=self.game.powerups
            )

        self.load_level()

    def load_level(self):
        # Reset the playfield and spawn a fresh copy of the level geometry.
        self.game.interface.update_level_details()

        # Clear out dynamic sprites while keeping the persistent player objects.
        self.balls.empty()
        self.bricks.empty()
        self.all_sprites.empty()
        self.balls.add(self.ball)
        self.all_sprites.add(self.paddle, self.ball)

        # Rebuild the block layout and restore the ball/paddle positions.
        self.spawn_blocks()
        self.paddle.reset()
        self.ball.reset()

        # Keep the HUD score text synchronized with the scoreboard model.
        self.game.interface.update_score(self.game.scoreboard.get_formatted_score())


        if self.game.levels.get_level().number == 1 and self.game.state == "ready":
            self.game.state = "login"
            self.login.toggle_state()

        else:

            self.game.state = "playing"



    def proceed_after_login(self):
        # The login popup hands control back to the play loop here.
        self.game.state = "playing"

    def spawn_blocks(self):
        # Build the grid layout for the current stage.
        cols = 9
        pad = 10
        brick_w, brick_h = 80, 29

        # Special bricks take multiple hits before they break.
        special_hits = {
            'powerup': 3,
            'hardened': 2,
            'volatile': 4
        }

        matrix_w = (brick_w * cols) + ((cols - 1) * pad)
        start_x = self.game.active_area.x + (self.game.active_area.width / 2) - (matrix_w / 2)
        start_y = self.game.active_area.y + 100

        # Pull the active level's layout data from the level manager.
        data = self.game.levels.get_level().layout

        for index, brick_type in enumerate(data):

            row = index // cols
            col = index % cols

            pos_x = start_x + (col * (brick_w + pad))
            pos_y = start_y + (row * (brick_h + pad))

            if brick_type == 'SKIP':
                continue

            hits = special_hits.get(brick_type, 1)
            large_block = brick_type in ['volatile', 'powerup', 'hardened']

            data_block = DataBlock(self.game, brick_type, position=(pos_x, pos_y),
                                   hits=hits, large_block=large_block)
            self.bricks.add(data_block)
            self.all_sprites.add(data_block)

    def spawn_additional_ball(self):
        # Clone the active ball so the multi-ball powerup can split the run.
        source = self.ball

        # Enable ball if inactive
        if source.state == 'inactive':
            source.enable()

        # Create clone
        clone = Ball(self.game, self.paddle, is_additional=True)
        clone.rect.center = source.rect.center
        clone.state = 'active'
        clone.visible = True
        clone.image = clone.frames[5]
        clone.base_speed = source.base_speed

        # Split trajectory
        new_vx = -source.speed[0]
        new_vy = source.speed[1]

        # If the primary was going perfectly vertical, give the clone a nudge
        if abs(new_vx) < 1:
            new_vx = 3

        # Normalize to ensure the clone matches the current game pace
        clone.speed[0], clone.speed[1] = MathUtils.set_magnitude(
            new_vx,
            new_vy,
            clone.base_speed
        )

        # Register the clone with the collision and render lists.
        self.balls.add(clone)
        self.all_sprites.add(clone)

        self.game.audio_manager.play_sfx('activate')


    def activate_powerup(self, key):
        # Map the keypress to a stored powerup slot.
        index = int(key - 1)

        try:
            powerup = self.powerups[index]
        except IndexError:
            return

        if powerup == 'multi':

            if len(self.balls) == 1:

                self.spawn_additional_ball()
                self.powerups.remove(powerup)

            else:

                self.game.interface.trigger_powerup_fail(index, time=500)

        elif powerup == 'speed':

            active_balls = [b for b in self.balls if b.state == 'active']

            if active_balls:

                self.game.audio_manager.play_sfx('activate')
                self.powerups.remove(powerup)

                for ball in active_balls:
                    if not ball.is_speed_boost:
                        ball.activate_speed_boost(multiplier=1.5, time=10000)

            else:

                self.game.interface.trigger_powerup_fail(index, time=500)


        elif powerup == 'health':

            if self.game.scoreboard.lives < 3:

                self.game.audio_manager.play_sfx('activate')
                self.powerups.remove(powerup)
                self.game.add_life()

            else:

                self.game.interface.trigger_powerup_fail(index, time=500)

        elif powerup == 'buffer':

            if not self.paddle.is_buffered:
                self.powerups.remove(powerup)
                self.paddle.activate_buffer(time=10000)
            else:
                self.game.interface.trigger_powerup_fail(index, time=500)

    def apply_rgb_split(self, surface, offset=4):
        # Split the image into red and cyan passes for the glitch effect.
        red_surf = surface.copy()
        cyan_surf = surface.copy()

        # Isolate channels using Pygame blend flags
        red_surf.fill((255, 0, 0), special_flags=pg.BLEND_RGBA_MULT)
        cyan_surf.fill((0, 255, 255), special_flags=pg.BLEND_RGBA_MULT)

        # Clear the original screen to prevent ghosting artifacts.
        surface.fill((0, 0, 0))

        # Blit the separated colors shifted in opposite directions
        surface.blit(cyan_surf, (-offset, 0))
        surface.blit(red_surf, (offset, 0), special_flags=pg.BLEND_RGBA_ADD)

    def apply_scanline_shift(self, surface, intensity=10, line_height=8):
        # Shift random scanlines horizontally to create a digital distortion effect.
        screen_w, screen_h = surface.get_size()
        temp_surf = surface.copy()

        # Loop down the screen row by row
        for y in range(0, screen_h, line_height):
            # Only glitch out random rows to keep it readable
            if random.random() < 0.3:
                # Pick a random pixel shift direction
                shift_x = random.randint(-intensity, intensity)

                # Define the source row rectangle
                row_rect = pg.Rect(0, y, screen_w, line_height)

                # Draw the shifted row back onto the screen
                surface.blit(temp_surf, (shift_x, y), row_rect)

    def apply_color_invert(self, surface):
        # Invert the current frame for a brief visual spike.
        inv = pg.Surface(surface.get_size())
        inv.fill((255, 255, 255))

        surface.blit(inv, (0, 0), special_flags=pg.BLEND_RGBA_SUB)


    def handle_events(self, events):
        # Route input to the active gameplay state and the modal overlays.
        for event in events:

            # Mouse Event
            if event.type == pg.MOUSEBUTTONDOWN and self.game.state == "playing":
                active_balls = [b for b in self.balls if b.state == "active"]
                if not active_balls and self.ball.state == 'inactive':
                    self.ball.enable()

            # Key Events
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    self.activate_powerup(key=1)
                elif event.key == pg.K_2:
                    self.activate_powerup(key=2)
                elif event.key == pg.K_3:
                    self.activate_powerup(key=3)
                elif event.key == pg.K_p:
                    self.pause.toggle_state()
                elif event.key == pg.K_q:

                    self.quit_confirm.show()

        # Popups
        if self.game.state == "login":
            self.login.handle_event(events)
        elif self.game.state == "playing" or self.game.state == "paused":
            self.pause.handle_event(events)
        elif self.game.state == "confirm_quit":
            self.quit_confirm.handle_event(events)
        elif self.game.state == "campaign_complete":
            self.no_more_levels.handle_event(events)
        elif self.game.state == "transitioning":
            self.completed.handle_event(events)

    def update(self):
        # Drive physics, collisions, and level completion state for the play section.
        if self.game.state == "playing":

            now = pg.time.get_ticks()
            self.game.physics.update_environment(now)

            if (not self.bricks
                and not self.explosions
                and not self.modules
                and not self.game.physics.glitch_active):

                if self.game.levels.index >= len(self.game.levels.levels) - 1:
                    self.game.state = "campaign_complete"
                    self.no_more_levels.show()
                else:
                    self.game.state = "transitioning"  # Change state immediately
                    self.completed.show() # Show level complete popup

        if self.game.state == "ready":
            self.game.state = 'playing'
            #self.load_level()
            self.start_new_level()

        if self.game.state in ["playing", "waiting_for_launch"]:
            self.game.physics.handle_collisions(
                game=self.game,
                paddle=self.paddle,
                balls=self.balls,
                bricks=self.bricks,
                modules=self.modules,
                powerups=self.powerups,
                explosion=Explosion,
                explosions=self.explosions,
                debris=Debris,
                all_sprites=self.all_sprites
            )
            self.all_sprites.update()

        # Popups
        if self.game.state == "transitioning":
            self.completed.update()

    def draw(self):
        # Draw the playfield first, then overlay any active popup state.
        self.game.interface.draw_game_hub()

        if not self.game.state == 'transitioning':
            self.all_sprites.draw(self.game.screen)

        # Popups
        if self.game.state == "login":
            self.login.draw()
        elif self.game.state == "paused":
            self.pause.draw()
        elif self.game.state == "confirm_quit":
            self.quit_confirm.draw()
        elif self.game.state == "campaign_complete":
            self.no_more_levels.draw()
        elif self.game.state == "transitioning":
            self.completed.draw()

        if self.game.physics.glitch_active:

            self.apply_scanline_shift(self.game.screen, intensity=15)

            pulse_offset = random.randint(2, 6)
            self.apply_rgb_split(self.game.screen, offset=pulse_offset)

            if random.random() < 0.05:
                self.apply_color_invert(self.game.screen)

        pg.display.flip()


class GameOverSection(Section):

    def __init__(self, game):
        super().__init__(game)

        self._load_assets()

    def _load_assets(self):
        # Game-over controls sit near the center of the screen.
        self.active_area = self.game.active_area
        area_center = (self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)

        self.restore_btn = Button(
            game=self.game,
            assets=['reload.png', 'reload_hover.png'],
            pos=(area_center[0], (area_center[1] + 125)),
            callback=self.restore_last_game
        )

        self.main_menu_btn = Button(
            game=self.game,
            assets=['menu.png', 'menu_hover.png'],
            pos=(area_center[0], (area_center[1] + 200)),
            callback=self.return_to_main_menu
        )

    def restore_last_game(self):
        # Rehydrate the most recent player profile back into the game state.
        player = self.game.players.auto_select_most_recent()

        if player:

            self.game.players.set_player(player.name)
            self.game.levels.set_level(player.level)

            print('player lives: ', player.lives)

            starting_lives = player.lives if player.lives > 0 else 1
            self.game.scoreboard.set_lives(starting_lives)
            self.game.scoreboard.set_score(player.score)
            self.game.powerups[:] = player.power_ups

            pg.mouse.set_visible(False)
            self.game.switch_section('play')
            self.game.state = 'ready'  # Boot into game
            self.game.sections['play'].load_level()  # Force level settings


    def return_to_main_menu(self):
        # Leave the game-over screen and return to the menu.
        self.game.switch_section("menu")

    def handle_events(self, events):
        # Buttons handle the navigation from the game-over screen.
        for event in events:

            self.restore_btn.handle_event(event)
            self.main_menu_btn.handle_event(event)

    def draw(self):
        # Draw the game-over background and navigation buttons.
        self.game.interface.draw_game_over_layout()
        self.restore_btn.draw()
        self.main_menu_btn.draw()
        pg.display.flip()
