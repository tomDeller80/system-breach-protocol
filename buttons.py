from core import Storage
import pygame as pg

class Button:

    def __init__(self, game, assets, pos, callback, scale=1):
        # Buttons are image-backed and swap frames on hover.
        self.game = game
        self.assets = assets
        self.scale = scale

        self.frames = self.generate_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

        self.callback = callback
        self.is_hovered = False

        self.screen = pg.display.get_surface()

    def generate_frames(self):
        # Load the normal and hover states from the button asset directory.
        frames = []
        for index, image in enumerate(self.assets):
           btn, _ = Storage.load_image(f"assets/buttons/{image}", scale=self.scale)
           frames.append(btn)
        return frames

    def handle_event(self, event):
        # Track hover state and fire the callback on a left click.
        if event.type == pg.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)

            if self.is_hovered and not was_hovered:
                self.game.audio_manager.play_sfx('hover')

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.game.audio_manager.play_sfx('click')
            self.callback()

    def draw(self):
        # Choose the correct frame for the current hover state.
        self.image = self.frames[1] if self.is_hovered else self.frames[0]
        render_rect = self.image.get_rect(center=self.rect.center)
        self.screen.blit(self.image, render_rect)
