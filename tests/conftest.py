import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _build_fake_pygame():
    pg = types.ModuleType("pygame")

    # Constants used by the project.
    pg.SRCALPHA = 1
    pg.RLEACCEL = 2
    pg.BLEND_RGBA_MULT = 3
    pg.BLEND_RGBA_ADD = 4
    pg.BLEND_RGBA_SUB = 5
    pg.SYSTEM_CURSOR_CROSSHAIR = 6

    pg.QUIT = 100
    pg.MOUSEBUTTONDOWN = 101
    pg.MOUSEBUTTONUP = 102
    pg.MOUSEMOTION = 103
    pg.KEYDOWN = 104

    pg.K_1 = 1
    pg.K_2 = 2
    pg.K_3 = 3
    pg.K_p = 16
    pg.K_q = 17
    pg.K_ESCAPE = 18
    pg.K_c = 19
    pg.K_BACKSPACE = 20
    pg.K_RETURN = 21

    class Rect:
        def __init__(self, x=0, y=0, w=0, h=0, **kwargs):
            self.x = x
            self.y = y
            self.width = w
            self.height = h
            for key, value in kwargs.items():
                setattr(self, key, value)

        @property
        def left(self):
            return self.x

        @left.setter
        def left(self, value):
            self.x = value

        @property
        def top(self):
            return self.y

        @top.setter
        def top(self, value):
            self.y = value

        @property
        def right(self):
            return self.x + self.width

        @right.setter
        def right(self, value):
            self.x = value - self.width

        @property
        def bottom(self):
            return self.y + self.height

        @bottom.setter
        def bottom(self, value):
            self.y = value - self.height

        @property
        def centerx(self):
            return self.x + self.width // 2

        @centerx.setter
        def centerx(self, value):
            self.x = value - self.width // 2

        @property
        def centery(self):
            return self.y + self.height // 2

        @centery.setter
        def centery(self, value):
            self.y = value - self.height // 2

        @property
        def center(self):
            return (self.centerx, self.centery)

        @center.setter
        def center(self, value):
            self.centerx, self.centery = value

        @property
        def size(self):
            return (self.width, self.height)

        def copy(self):
            return Rect(self.x, self.y, self.width, self.height)

        def collidepoint(self, pos):
            x, y = pos
            return self.left <= x < self.right and self.top <= y < self.bottom

        def colliderect(self, other):
            return not (
                self.right <= other.left
                or self.left >= other.right
                or self.bottom <= other.top
                or self.top >= other.bottom
            )

        def inflate(self, size):
            if isinstance(size, tuple):
                dw, dh = size
            else:
                dw = dh = size
            return Rect(
                self.x - dw // 2,
                self.y - dh // 2,
                self.width + dw,
                self.height + dh,
            )

        def clamp_ip(self, area):
            if self.left < area.left:
                self.left = area.left
            if self.top < area.top:
                self.top = area.top
            if self.right > area.right:
                self.right = area.right
            if self.bottom > area.bottom:
                self.bottom = area.bottom

    class Surface:
        def __init__(self, size=(0, 0), flags=0):
            self._size = (int(size[0]), int(size[1]))
            self._alpha = 255

        def get_size(self):
            return self._size

        def get_width(self):
            return self._size[0]

        def get_height(self):
            return self._size[1]

        def get_rect(self, **kwargs):
            rect = Rect(0, 0, self._size[0], self._size[1])
            for key, value in kwargs.items():
                setattr(rect, key, value)
            return rect

        def fill(self, *args, **kwargs):
            return self

        def blit(self, *args, **kwargs):
            return self

        def copy(self):
            return Surface(self._size)

        def convert_alpha(self):
            return self

        def set_colorkey(self, *args, **kwargs):
            return None

        def set_alpha(self, value, *args, **kwargs):
            self._alpha = value
            return None

    class Font:
        def __init__(self, filename, font_size):
            self.filename = filename
            self.font_size = font_size

        def render(self, text, antialias, color):
            width = max(1, len(str(text)) * max(4, self.font_size // 2))
            return Surface((width, self.font_size + 6))

    class DummySound:
        def play(self):
            return None

    class _Music:
        def load(self, *args, **kwargs):
            return None

        def play(self, *args, **kwargs):
            return None

        def pause(self):
            return None

        def unpause(self):
            return None

        def stop(self):
            return None

        def fadeout(self, *args, **kwargs):
            return None

        def set_volume(self, *args, **kwargs):
            return None

        def get_volume(self):
            return 1.0

    class _Display:
        def __init__(self):
            self._surface = Surface((1, 1))

        def init(self):
            return None

        def set_mode(self, size):
            self._surface = Surface(size)
            return self._surface

        def get_surface(self):
            return self._surface

        def set_caption(self, *args, **kwargs):
            return None

        def set_icon(self, *args, **kwargs):
            return None

        def flip(self):
            return None

    class _Mouse:
        def __init__(self):
            self._pos = (0, 0)

        def set_visible(self, *args, **kwargs):
            return None

        def set_cursor(self, *args, **kwargs):
            return None

        def set_pos(self, *args):
            if len(args) == 1:
                self._pos = args[0]
            elif len(args) >= 2:
                self._pos = (args[0], args[1])

        def get_pos(self):
            return self._pos

    class _EventModule:
        def __init__(self):
            self._queue = []

        def get(self):
            queue = self._queue[:]
            self._queue.clear()
            return queue

        def set_grab(self, *args, **kwargs):
            return None

        def Event(self, type, dict=None):
            event = SimpleNamespace(type=type)
            if dict:
                for key, value in dict.items():
                    setattr(event, key, value)
            return event

    class _Time:
        def get_ticks(self):
            import time

            return int(time.time() * 1000)

    class Clock:
        def tick(self, *args, **kwargs):
            return None

    class _Image:
        def load(self, filename):
            return Surface((32, 32))

    class _Transform:
        def scale(self, surface, size):
            return Surface(size)

    class _Draw:
        def rect(self, *args, **kwargs):
            return None

    class Sprite:
        def __init__(self):
            self._groups = []

        def kill(self):
            for group in list(self._groups):
                if self in group._sprites:
                    group._sprites.remove(self)
            self._groups.clear()

    class Group:
        def __init__(self, *sprites):
            self._sprites = []
            self.add(*sprites)

        def add(self, *sprites):
            for sprite in sprites:
                if sprite not in self._sprites:
                    self._sprites.append(sprite)
                    if hasattr(sprite, "_groups"):
                        sprite._groups.append(self)

        def empty(self):
            for sprite in list(self._sprites):
                if hasattr(sprite, "_groups") and self in sprite._groups:
                    sprite._groups.remove(self)
            self._sprites.clear()

        def update(self):
            for sprite in list(self._sprites):
                if hasattr(sprite, "update"):
                    sprite.update()

        def draw(self, *args, **kwargs):
            return None

        def __iter__(self):
            return iter(self._sprites)

        def __len__(self):
            return len(self._sprites)

        def __bool__(self):
            return bool(self._sprites)

        def __contains__(self, item):
            return item in self._sprites

    def spritecollide(sprite, group, dokill=False):
        hits = [item for item in group if hasattr(item, "rect") and sprite.rect.colliderect(item.rect)]
        if dokill:
            for item in hits:
                item.kill()
        return hits

    class _FontModule:
        def init(self):
            return None

        def get_fonts(self):
            return ["exo2"]

        def Font(self, filename, font_size):
            return Font(filename, font_size)

    class _MixerModule:
        def __init__(self):
            self.music = _Music()

        def init(self):
            return None

        def get_init(self):
            return True

        def Sound(self, *args, **kwargs):
            return DummySound()

    def init():
        return (0, 0)

    def quit():
        return None

    pg.Rect = Rect
    pg.Surface = Surface
    pg.sprite = types.SimpleNamespace(Sprite=Sprite, Group=Group, RenderPlain=Group, spritecollide=spritecollide)
    pg.display = _Display()
    pg.mouse = _Mouse()
    pg.event = _EventModule()
    pg.time = _Time()
    pg.time.Clock = Clock
    pg.font = _FontModule()
    pg.image = _Image()
    pg.transform = _Transform()
    pg.draw = _Draw()
    pg.mixer = _MixerModule()
    pg.Clock = Clock
    pg.init = init
    pg.quit = quit

    return pg


sys.modules["pygame"] = _build_fake_pygame()

import pygame as pg
import pytest

from core import Storage


pg.init()
pg.display.init()
pg.display.set_mode((1280, 720))
pg.font.init()


@pytest.fixture
def asset_stubs(monkeypatch):
    def load_image(filename, colorkey=None, scale=1):
        width = max(1, int(32 * scale))
        height = max(1, int(32 * scale))
        surface = pg.Surface((width, height), pg.SRCALPHA)
        return surface, surface.get_rect()

    def load_font(filename, font_size=24):
        return pg.font.Font(filename, font_size)

    def load_sound(filename):
        return filename

    monkeypatch.setattr(Storage, "load_image", staticmethod(load_image))
    monkeypatch.setattr(Storage, "load_font", staticmethod(load_font))
    monkeypatch.setattr(Storage, "load_sound", staticmethod(load_sound))
    return SimpleNamespace()
