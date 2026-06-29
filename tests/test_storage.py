import json

import pygame as pg

from core import Storage


def test_load_image_returns_scaled_surface(monkeypatch):
    source = pg.Surface((20, 10), pg.SRCALPHA)
    source.fill((10, 20, 30, 255))

    monkeypatch.setattr(Storage, "get_storage_path", staticmethod(lambda *args, **kwargs: "dummy.png"))
    monkeypatch.setattr(pg.image, "load", lambda *args, **kwargs: source.copy())

    image, rect = Storage.load_image("assets/test.png", scale=2)

    assert image.get_size() == (40, 20)
    assert rect.size == (40, 20)


def test_load_sound_returns_pygame_sound(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(Storage, "get_storage_path", staticmethod(lambda *args, **kwargs: "dummy.wav"))
    monkeypatch.setattr(pg.mixer, "get_init", lambda: True)
    monkeypatch.setattr(pg.mixer, "Sound", lambda *args, **kwargs: sentinel)

    assert Storage.load_sound("assets/test.wav") is sentinel


def test_load_font_returns_pygame_font(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(Storage, "get_storage_path", staticmethod(lambda *args, **kwargs: "dummy.ttf"))
    monkeypatch.setattr(pg.font, "get_fonts", lambda: ["exo2"])
    monkeypatch.setattr(pg.font, "Font", lambda *args, **kwargs: sentinel)

    assert Storage.load_font("assets/test.ttf", font_size=18) is sentinel


def test_read_and_write_json(monkeypatch, tmp_path):
    path = tmp_path / "sample.json"
    data = {"scores": [1, 2, 3]}
    path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(Storage, "get_storage_path", staticmethod(lambda *args, **kwargs: str(path)))

    assert Storage.read_json("sample.json", is_static=False) == data

    payload = {"scores": [9]}
    Storage.write_json("sample.json", payload)
    assert json.loads(path.read_text(encoding="utf-8")) == payload
