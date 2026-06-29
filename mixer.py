from core import Storage
import pygame as pg

class AudioManager:
    def __init__(self):
        # Initialize the audio subsystem before any sounds are loaded.
        pg.mixer.init()

        self.sounds = {}
        self.music_tracks = {}

        self.load_assets()

    def load_assets(self):
        # Cache every sound effect once so gameplay can trigger them cheaply.
        self.sounds['purge'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/power-down.wav'))
        self.sounds['hit-paddle'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/hit_paddle.wav'))
        self.sounds['hit-block'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/hit_block.wav'))
        self.sounds['explosion'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/explosion.wav'))
        self.sounds['powerup'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/powerup.wav'))
        self.sounds['click'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/click.wav'))
        self.sounds['hover'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/hover.wav'))
        self.sounds['denied'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/denied.wav'))
        self.sounds['activate'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/activate.wav'))
        self.sounds['pip'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/pip.wav'))
        self.sounds['success'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/success.wav'))
        self.sounds['plasma'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/plasma.wav'))
        self.sounds['glitch'] = pg.mixer.Sound(Storage.load_sound('assets/sfx/glitch.wav'))

        # Store music paths separately because pygame loads music by filename.
        self.music_tracks['synthwav'] = Storage.get_storage_path('assets/music/soundtrack-341853.mp3', True)
        # Example: self.music_tracks['synthwav'].set_volume(0.6)

    def play_music(self, track_key='synthwav', loops=-1):
        # Load and start the requested track with a fade-in.
        pg.mixer.music.load(self.music_tracks[track_key])
        pg.mixer.music.play(loops, fade_ms=2000)

    def pause_music(self):
        # Temporarily suspend the current music track.
        pg.mixer.music.pause()

    def unpause_music(self):
        # Resume playback after pause.
        pg.mixer.music.unpause()

    def stop_music(self):
        # Hard-stop the current track.
        pg.mixer.music.stop()

    def fadeout_music(self, time=2000):
        # Let the current track decay cleanly instead of cutting it off.
        pg.mixer.music.fadeout(time)

    def get_music_volume(self):
        # Read back the current global music volume.
        return pg.mixer.music.get_volume()

    def set_music_volume(self, volume=1):
        # Clamp is handled by pygame, so forward the requested volume directly.
        pg.mixer.music.set_volume(volume)

    def play_sfx(self, sfx_key, volume=1):
        # Play a cached sound effect if the key exists.
        if sfx_key in self.sounds:
            self.sounds[sfx_key].play()
