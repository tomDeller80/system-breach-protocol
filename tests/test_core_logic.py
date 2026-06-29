from types import SimpleNamespace

import pygame as pg

from core import Storage
from levels import Level, Levels
from scoreboard import Scoreboard
from utils.maths import apply_friction, calculate_redirected_velocity, set_magnitude
from utils.physics import calculate_bounce_speed, calculate_smooth_follow
from core.physics_engine import PhysicsEngine


def test_scoreboard_tracks_score_and_lives():
    board = Scoreboard()

    board.update(150)
    board.lose_life()
    board.gain_life()
    board.set_score(900)
    board.set_lives(2)

    assert board.get_score() == 900
    assert board.get_lives() == 2
    assert board.get_formatted_score() == "0000900"


def test_levels_loads_and_advances(monkeypatch):
    data = {
        "levels": {
            "1": {"title": "Alpha", "modules": ["A", "B"]},
            "2": {"title": "Beta", "modules": ["C"]},
        }
    }

    monkeypatch.setattr(Storage, "read_json", staticmethod(lambda *args, **kwargs: data))

    levels = Levels()

    assert [level.title for level in levels.levels] == ["Alpha", "Beta"]
    assert levels.get_level().title == "Alpha"

    levels.set_level("Beta")
    assert levels.get_level().title == "Beta"

    levels.reset()
    assert levels.get_level().title == "Alpha"


def test_level_is_plain_data():
    level = Level(3, "Gamma", ["X", "Y"])

    assert level.number == 3
    assert level.title == "Gamma"
    assert level.layout == ["X", "Y"]


def test_math_helpers():
    assert apply_friction(10, 0.5) == 5
    assert set_magnitude(3, 4, 10) == (6.0, 8.0)

    vx, vy = calculate_redirected_velocity(2, 5, 3, 0.5, 6, 10)
    assert round((vx * vx + vy * vy) ** 0.5, 5) == 10
    assert vy < 0


def test_physics_helpers():
    dummy = SimpleNamespace(rect=pg.Rect(10, 10, 20, 20))
    area = pg.Rect(0, 0, 100, 100)

    assert calculate_smooth_follow(0, 10, 0, 20, 0.5, 1.0) == (5.0, 5.0)
    assert calculate_bounce_speed(dummy, area, 4, -6) == (4, -6)

    dummy.rect.left = -1
    dummy.rect.top = -1
    assert calculate_bounce_speed(dummy, area, 4, -6) == (-4, 6)


def test_physics_engine_glitch_toggles():
    engine = PhysicsEngine()
    engine.activate_glitch()
    assert engine.glitch_active is True

    engine.update_environment(engine.glitch_start_time + engine.glitch_duration + 1)
    assert engine.glitch_active is False
    assert engine.glitch_factor == 1.0
