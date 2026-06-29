from core import Storage
import pygame as pg
from buttons import Button

# Modal overlays for login, pause, and level-complete flows.
class Popup:
    def __init__(self, game, area):
        # Shared popup state and drawing surface.
        self.game = game
        self.active_area = area
        self.screen = pg.display.get_surface()

    def handle_event(self, event):
        pass

    def draw(self):
        pass

class Login(Popup):

    def __init__(self, game, area):

        super().__init__(game, area)

        # State
        self.is_visible = False

        # Instantiate Assets
        self.load_image_assets()
        self.load_fonts()

        # --------------------------------------------------------------
        #  Player List and Current Index
        # --------------------------------------------------------------
        self.existing_players = self.game.players.players
        self.selected_user_index = 0

        # Layout Geometry / Position
        self.rect = self.bg_image.get_rect(center=area.center)

        # -------------------------------
        #   Terminal & Text Input State
        # -------------------------------
        self.username = ""
        self.max_chars = 10
        self.is_terminal_active = True  # Focus starts on the input box

        # Cursor Blinking State
        self.cursor_visible = True
        self.last_cursor_toggle = pg.time.get_ticks()
        self.cursor_interval = 500  # Blink every 500ms

        # UI Component Rectangles for Event Collision
        self.input_rect = pg.Rect(self.rect.left + 50, self.rect.top + 150, 410, 250)

        # ----------------------------------
        #    SCROLLABLE CONTAINER CONFIG
        # ----------------------------------

        # The visible frame area matching the right terminal cutout box
        self.list_view_rect = pg.Rect(self.rect.left + 520, self.rect.top + 145, 335, 260)

        # Geometry constants for each individual player item block
        self.slot_w, self.slot_h = 360, 75
        self.slot_spacing = 15
        self.total_item_h = self.slot_h + self.slot_spacing

        # Calculate container size needed for all user records
        self.container_h = max(len(self.existing_players) * self.total_item_h, self.list_view_rect.height)
        self.container_surface = pg.Surface((self.slot_w, self.container_h), pg.SRCALPHA)

        # Scroll Tracking Variables
        self.scroll_y = 0  # Current top pixel offset of the visible window
        self.max_scroll = max(0, self.container_h - self.list_view_rect.height)
        self.scroll_speed = 25

        # Scrollbar Track Geometry (Right edge of the panel box)
        self.track_rect = pg.Rect(self.list_view_rect.right, self.list_view_rect.top, 12,
                                  self.list_view_rect.height)
        self.scroller_rect = self.scroller_image.get_rect(x=self.track_rect.x)
        self.update_scrollbar_position()

        # Interaction Flag
        self.is_dragging_scrollbar = False

        # Buttons
        self.btn_execute = Button(
            game=self.game,
            assets=['execute.png', 'execute_hover.png'],
            pos=(self.rect.left + 225, self.rect.top + 470),
            callback=lambda: self.add_user(self.username)
        )
        self.btn_assume = Button(
            game=self.game,
            assets=['assume.png', 'assume_hover.png'],
            pos=(self.rect.left + 700, self.rect.top + 470),
            callback=self.assume_selected_user
        )

    def load_image_assets(self):
        self.bg_image, _ = Storage.load_image(filename='assets/popups/login_bg.png', scale=1)
        self.player_panel, _ = Storage.load_image(filename='assets/popups/player_entry.png', scale=1)
        self.player_panel_hover, _ = Storage.load_image(filename='assets/popups/player_entry_hover.png', scale=1)
        self.heart_image, _ = Storage.load_image(filename='assets/popups/life.png', scale=1)
        self.scroller_image, _ = Storage.load_image(filename='assets/popups/scroller.png', scale=1)


    def load_fonts(self):
        self.color_neon_cyan = (0, 255, 204)
        self.color_white = (240, 240, 240)
        self.color_neon_green = (0, 255, 204)
        self.color_red = (255, 0, 0)

        self.name_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=24)
        self.sub_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=16)
        self.terminal_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=22)

        self.txt_awaiting = self.terminal_font.render("Awaiting handshake ...", True, self.color_white)
        self.txt_enter_id = self.terminal_font.render("Enter ID hash:", True, self.color_white)

    def update_scrollbar_position(self):
        """Calculates where the scroller handle graphic belongs on the track rail."""
        if self.max_scroll == 0:
            self.scroller_rect.y = self.track_rect.y
            return

        # Linear percentage map: travel distance ratio
        scroll_ratio = self.scroll_y / self.max_scroll
        available_track = self.track_rect.height - self.scroller_rect.height
        self.scroller_rect.y = self.track_rect.y + int(scroll_ratio * available_track)

    def update_terminal_status(self, message, type="normal"):
        # default message colour
        font_colour = self.color_white

        if type == "error":
            font_colour = self.color_red

        self.txt_awaiting = self.terminal_font.render(f"{message.strip()}", True, font_colour)


    def terminal_entry(self, unicode_char):

        if len(self.username) < self.max_chars:
            # Simple alphanumeric validation
            if unicode_char.isalnum() or unicode_char in ['_', '-']:
                self.username += unicode_char.upper()
                self.game.audio_manager.play_sfx('pip')  # Match your keypress sound


    def add_user(self, name):

        if not name.strip():
            return

        # Check if user already exists
        for user in self.existing_players:
            if user.name == name:
                self.update_terminal_status(message="User name already exists ...", type="error")
                return

        # Add new user profile with starting stats: (Name, Level, Lives)
        level_title = self.game.levels.levels[0].title
        params = {"name":name, "level":level_title, "lives":3, "score":0}




        new_profile = self.game.players.add_player(params)

        # Auto-select the newly created user and transition
        self.username = ""
        self.select_user(new_profile)


    def assume_selected_user(self):
        # Guard against empty saved profile lists before dereferencing the current selection.
        if not self.existing_players:
            self.update_terminal_status(message="No saved users available ...", type="error")
            return

        if self.selected_user_index >= len(self.existing_players):
            self.selected_user_index = 0

        self.select_user(self.existing_players[self.selected_user_index])


    def select_user(self, user_profile):

        if not user_profile or len(self.game.players.players) == 0:
            return

        # Set game global parameters based on chosen profile
        self.game.players.set_player(user_profile.name)
        self.game.levels.set_level(user_profile.level)

        self.game.scoreboard.set_lives(user_profile.lives)
        self.game.scoreboard.set_score(user_profile.score)
        self.game.powerups[:] = user_profile.power_ups

        self.game.sections['play'].load_level() # Force level settings

        self.game.audio_manager.play_sfx('success')
        self.game.state = 'ready'  # Boot into game

        # ----- Hide Popup ------
        self.hide()


    def handle_event(self, events):

        for event in events:
            # Mouse Wheel Scrolling over the user list target frame
            if event.type == pg.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # ------------------------------
                #   LEFT SIDE: TERMINAL
                # ------------------------------

                # Check Text Box Focus Click
                if self.input_rect.collidepoint((mx, my)):
                    self.is_terminal_active = True
                else:
                    self.is_terminal_active = False

                # Handle Cursor Blink Logic
                now = pg.time.get_ticks()
                if now - self.last_cursor_toggle > self.cursor_interval:
                    self.cursor_visible = not self.cursor_visible
                    self.last_cursor_toggle = now

                # Determine the trailing character
                # Use a solid block '█' or a vertical pipe '|' to match your mockup
                cursor_char = "█" if (self.cursor_visible and self.is_terminal_active) else ""

                # Render the whole string combined
                display_text = f"> {self.username}{cursor_char}"
                txt_render = self.terminal_font.render(display_text, True, self.color_neon_green)

                self.screen.blit(txt_render, (self.input_rect.left + 20, self.input_rect.top + 110))

                # ------------------------------
                #   RIGHT SIDE: PLAYER LIST
                # ------------------------------

                # Handle Mouse Scrolling Over Player List
                if self.list_view_rect.collidepoint((mx, my)):
                    if event.button == 4:  # Scroll Up
                        self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                        self.update_scrollbar_position()
                    elif event.button == 5:  # Scroll Down
                        self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                        self.update_scrollbar_position()

                # Handle Drag Initialization on Scroller Thumb
                if event.button == 1:
                    if self.scroller_rect.collidepoint((mx, my)):
                        self.is_dragging_scrollbar = True

                    # Handle Click Selections inside the lists view frame
                    elif self.list_view_rect.collidepoint((mx, my)):
                        # Re-calculate hit target matching the scrolled local position space
                        local_my = my - self.list_view_rect.top + self.scroll_y
                        clicked_index = local_my // self.total_item_h

                        if clicked_index < len(self.existing_players):
                            self.selected_user_index = clicked_index
                            self.game.audio_manager.play_sfx('pip')

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_scrollbar = False

            elif event.type == pg.MOUSEMOTION:
                # Track mouse drag sliding coordinates
                if self.is_dragging_scrollbar:
                    _, my = event.pos
                    available_track = self.track_rect.height - self.scroller_rect.height

                    # Clamp the scroller button inside the track track limits
                    relative_y = max(0, min(my - self.track_rect.top, available_track))
                    self.scroller_rect.y = self.track_rect.top + relative_y

                    # Map scroller location back onto the surface scroll view depth
                    scroll_ratio = relative_y / available_track if available_track > 0 else 0
                    self.scroll_y = int(scroll_ratio * self.max_scroll)

            elif event.type == pg.KEYDOWN and self.is_terminal_active:
                # Handle Active Keyboard Input
                if event.key == pg.K_BACKSPACE:
                    self.username = self.username[:-1]
                    self.game.audio_manager.play_sfx('pip')
                elif event.key == pg.K_RETURN:
                    self.add_user(self.username)
                else:
                    self.terminal_entry(event.unicode)

            # Buttons
            self.btn_execute.handle_event(event)
            self.btn_assume.handle_event(event)

    def render_container_surface(self):

        self.container_surface.fill((0, 0, 0, 0))  # Maintain transparency background

        # Iterate player list from latest entry first
        for i, user in reversed(list(enumerate(self.existing_players))):

            slot_y = i * self.total_item_h

            # 1. Base Module Frame Panel
            if i == self.selected_user_index:
                self.container_surface.blit(self.player_panel_hover, (0, slot_y))
            else:
                self.container_surface.blit(self.player_panel, (0, slot_y))

            # 2. Text Details
            txt_name = self.name_font.render(user.name, True, self.color_neon_cyan)
            txt_lvl = self.sub_font.render(f"Level : {user.level}", True, self.color_neon_cyan)

            self.container_surface.blit(txt_name, (20, slot_y + 12))
            self.container_surface.blit(txt_lvl, (20, slot_y + 44))

            # 3. Dynamic Heart Icons Loop
            for h in range(user.lives):
                heart_x = self.slot_w - 130 + (h * 26)
                self.container_surface.blit(self.heart_image, (heart_x, slot_y + 18))

    def reset(self):
        self.is_visible = False
        self.username = ""
        self.is_terminal_active = True
        self.cursor_visible = True
        self.scroll_y = 0
        self.update_terminal_status(message="Awaiting handshake...")


    def show(self):
        self.is_visible = True
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)

    def hide(self):
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        self.reset()
        self.game.sections['play'].proceed_after_login()

    def toggle_state(self):

        if self.is_visible:
            self.hide()
        else:
            self.show()

    def draw(self):

        if not self.is_visible:
            return

        # Draw Primary Interface Template Background
        self.screen.blit(self.bg_image, self.rect)

        # ------------------------------
        #   LEFT SIDE: TERMINAL DRAW
        # ------------------------------

        # Intro lines
        self.screen.blit(self.txt_awaiting, (self.input_rect.left + 20, self.input_rect.top + 30))
        self.screen.blit(self.txt_enter_id, (self.input_rect.left + 20, self.input_rect.top + 80))

        # Dynamic name typing draw
        txt_prefix = self.terminal_font.render("> ", True, self.color_neon_green)
        txt_name = self.terminal_font.render(self.username, True, self.color_neon_green)

        self.screen.blit(txt_prefix, (self.input_rect.left + 20, self.input_rect.top + 110))
        self.screen.blit(txt_name, (self.input_rect.left + 40, self.input_rect.top + 110))

        # Animate Terminal Cursor Block
        now = pg.time.get_ticks()
        if now - self.last_cursor_toggle > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = now

        if self.cursor_visible and self.is_terminal_active:
            cursor_x = self.input_rect.left + 40 + txt_name.get_width() + 4
            cursor_rect = pg.Rect(cursor_x, self.input_rect.top + 114, 12, 22)
            pg.draw.rect(self.screen, self.color_neon_green, cursor_rect)


        # --------------------------------------
        #    RIGHT SIDE: USER LIST ITEMS DRAW
        # --------------------------------------

        # Refresh & Blit the Scrolled Content Region
        self.render_container_surface()
        self.screen.blit(self.container_surface, self.list_view_rect,
                         area=pg.Rect(0, self.scroll_y, self.list_view_rect.width, self.list_view_rect.height))

        # Render Scroller Track Elements
        self.screen.blit(self.scroller_image, self.scroller_rect)

        # Buttons
        self.btn_execute.draw()
        self.btn_assume.draw()


class Pause(Popup):

    def __init__(self, game, area):
        super().__init__(game, area)

        # Game state
        self.last_game_state = self.game.state

        # Image / Rect
        self.image, self.rect = Storage.load_image(filename='assets/popups/pause.png', scale=0.75)

        # Flag
        self.is_paused = False

        # Position
        self.rect.center = area.center

    def pause(self):
        # Freeze the game loop state and pause the music.
        self.is_paused = True
        self.last_game_state = self.game.state
        self.game.audio_manager.pause_music()
        self.game.state = 'paused'

    def unpause(self):
        # Restore the last active game state and resume audio.
        self.game.state = self.last_game_state
        self.game.audio_manager.unpause_music()
        self.is_paused = False

    def toggle_state(self):

        if self.is_paused:
            self.unpause()
        else:
            self.pause()


    def handle_event(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_paused:
                    self.unpause()

    def draw(self):
        if self.is_paused:
            self.screen.blit(self.image, self.rect)


class QuitConfirm(Popup):

    def __init__(self, game, area):
        super().__init__(game, area)

        # Game state
        self.last_game_state = self.game.state

        # Image / Rect
        self.image, self.rect = Storage.load_image(filename='assets/popups/terminate.png', scale=0.75)
        # Flag
        self.is_visible = False

        # Position
        self.rect.center = area.center


        # Initialise Buttons
        self.initialise_buttons()


    def initialise_buttons(self):

       # Buttons are intentionally explicit so the flow is obvious in the UI.
       self.btn_main_menu = Button(
           game=self.game,
           assets=['yes_quit.png', 'yes_quit_hover.png'],
           scale=0.6,
           pos=(self.rect.centerx - 100, self.rect.bottom - 40),
           callback=self.return_to_main_menu
       )

       self.btn_cancel = Button(
            game=self.game,
            assets=['cancel.png', 'cancel_hover.png'],
            scale=0.6,
            pos=(self.rect.centerx + 100, self.rect.bottom - 40),
            callback=self.cancel
       )

    def show(self):

        self.is_visible = True
        self.last_game_state = self.game.state
        self.game.audio_manager.pause_music()
        self.game.state = 'confirm_quit'
        pg.mouse.set_visible(True)

    def toggle_state(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def hide(self):
        # Return to the last game state and resume audio if the player cancels.
        self.game.state = self.last_game_state
        self.game.audio_manager.unpause_music()
        self.is_visible = False
        pg.mouse.set_visible(False)

    def return_to_main_menu(self):
        # Leave the run and send the player back to the main menu.
        self.is_visible = False
        self.game.audio_manager.play_music()
        self.game.switch_section("menu")

    def cancel(self):
        # Close the confirmation popup and resume the game.
        self.hide()

    def handle_event(self, events):
        # Only react while the confirmation dialog is visible.
        if not self.is_visible:
            return

        for event in events:
            self.btn_main_menu.handle_event(event)
            self.btn_cancel.handle_event(event)

            if event.type == pg.KEYDOWN and event.key in (pg.K_ESCAPE, pg.K_c):
                self.cancel()

    def draw(self):

        if self.is_visible:
            self.screen.blit(self.image, self.rect)

            self.btn_main_menu.draw()
            self.btn_cancel.draw()


class NoMoreLevels(Popup):

    def __init__(self, game, area):
        super().__init__(game, area)

        self.last_game_state = self.game.state
        self.image, self.rect = Storage.load_image(filename='assets/popups/congratulations.png', scale=0.75)
        self.is_visible = False
        self.rect.center = area.center

        self.initialise_buttons()

    def initialise_buttons(self):

        self.btn_main_menu = Button(
            game=self.game,
            assets=['main_menu.png', 'main_menu_hover.png'],
            scale=0.7,
            pos=(self.rect.centerx - 100, self.rect.bottom - 30),
            callback=self.return_to_main_menu
        )

        self.btn_scoreboard = Button(
            game=self.game,
            assets=['scoreboard.png', 'scoreboard_hover.png'],
            scale=0.7,
            pos=(self.rect.centerx + 100, self.rect.bottom - 30),
            callback=self.open_scoreboard
        )

    def show(self):
        self.is_visible = True
        self.last_game_state = self.game.state
        self.game.audio_manager.pause_music()
        self.game.state = 'campaign_complete'
        pg.mouse.set_visible(True)

    def hide(self):
        self.game.state = self.last_game_state
        self.game.audio_manager.unpause_music()
        self.is_visible = False
        pg.mouse.set_visible(False)

    def toggle_state(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def return_to_main_menu(self):
        self.is_visible = False
        self.game.audio_manager.play_music()
        self.game.switch_section("menu")

    def open_scoreboard(self):
        self.is_visible = False
        self.game.audio_manager.play_music()
        self.game.switch_section("score")

    def handle_event(self, events):
        if not self.is_visible:
            return

        for event in events:
            self.btn_main_menu.handle_event(event)
            self.btn_scoreboard.handle_event(event)

    def draw(self):
        if self.is_visible:
            self.screen.blit(self.image, self.rect)
            self.btn_main_menu.draw()
            self.btn_scoreboard.draw()



class Completed(Popup):

    def __init__(self, game, area):
        super().__init__(game, area)

        # Assets
        self.image, self.rect = Storage.load_image(filename='assets/popups/completed.png', scale=1)
        self.image1 = self.image
        self.image2, _ = Storage.load_image(filename='assets/popups/completed2.png', scale=1)
        self.pip_image, _ = Storage.load_image(filename='assets/popups/pip.png', scale=1)

        # Font
        self.percent_font = Storage.load_font(filename='assets/fonts/Exo2-Bold.ttf', font_size=28)
        self.primary_neon = (0, 243, 255)

        # Flags
        self.is_visible = False

        # Popup Position
        self.rect.center = area.center

        # Animation Parameters
        self.percentage = self.percent_font.render(f"000%", True, self.primary_neon)
        self.max_pips = 42 # Number or pips
        self.percent_val= 0 # Percentage (%)
        self.increment = 100 / self.max_pips
        self.current_visible_pips = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 20

        # Pip position
        self.pip_x = area.center[0] + 17
        self.pip_y = area.center[1] + 77

        # Percentage position
        self.percent_x = area.center[0] - 85
        self.percent_y = area.center[1] + 70


    def reset(self):
        # Clear the animation state so the popup can be shown again.
        self.is_visible = False
        self.percent_val = 0  # Percentage (%)
        self.current_visible_pips = 0 # Visible pips
        self.image = self.image1

    def show(self):
        # Begin the level-complete sequence and fade the music out.
        self.is_visible = True
        self.game.audio_manager.fadeout_music()

    def hide(self):
        # Return to the ready state once the popup is dismissed.
        self.game.audio_manager.play_music()
        self.game.state = 'ready'
        self.reset()

    def toggle_state(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def handle_event(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_visible:
                    self.hide()

    def update(self):
        # Increment the completion meter until the finale image is reached.
        if not self.is_visible:
            return

        now = pg.time.get_ticks()
        # Increment the counter based on time
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            if self.current_visible_pips < self.max_pips:
                self.current_visible_pips += 1
                self.game.audio_manager.play_sfx('pip')
                self.percent_val += self.increment
                self.percentage = self.percent_font.render(f"{round(self.percent_val):03}%", True, self.primary_neon)

                if self.current_visible_pips == self.max_pips:
                    self.game.audio_manager.play_sfx('success')
                    self.image = self.image2

    def draw_pips(self):
        # Draw the visible completion indicators one by one.
        x = self.pip_x
        for index in range(self.current_visible_pips):
            self.screen.blit(self.pip_image, (x, self.pip_y))
            x += 7  # Spacing


    def draw(self):
        # Overlay the completion popup and its animated progress state.
        if self.is_visible:
            self.screen.blit(self.image, self.rect)
            self.screen.blit(self.percentage, dest=(self.percent_x, self.percent_y))
            self.draw_pips()
