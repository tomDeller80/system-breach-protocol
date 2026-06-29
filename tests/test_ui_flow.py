from types import SimpleNamespace

import pygame as pg

from core import Storage
from sections import ScoreMenuSection
from systembreach import SystemBreach


class RecordingInterface:
    def __init__(self):
        self.results = None
        self.draw_calls = 0

    def draw_scoreboard_layout(self):
        self.draw_calls += 1

    def draw_score_results(self, results):
        self.results = list(results)


def test_score_menu_refreshes_without_restart():
    players = [
        SimpleNamespace(name="ALPHA", score=100, last_played="2026-01-01T00:00:00"),
    ]
    game = SimpleNamespace(
        players=SimpleNamespace(players=players),
        interface=RecordingInterface(),
        screen=pg.display.get_surface(),
    )

    section = ScoreMenuSection(game)
    players.append(SimpleNamespace(name="BETA", score=250, last_played="2026-01-02T00:00:00"))
    section.draw()

    assert game.interface.draw_calls == 1
    assert game.interface.results[0].name == "BETA"
    assert len(game.interface.results) == 2


def test_systembreach_bootstraps(monkeypatch, asset_stubs):
    def fake_read_json(json_file, is_static=True):
        if json_file == "players.json":
            return {"players": {}}
        if json_file == "data/levels.json":
            return {
                "levels": {
                    "1": {"title": "Boot", "modules": ["SKIP"] * 9},
                }
            }
        return {}

    monkeypatch.setattr(Storage, "read_json", staticmethod(fake_read_json))
    monkeypatch.setattr(Storage, "write_json", staticmethod(lambda *args, **kwargs: None))

    game = SystemBreach()

    assert "menu" in game.sections
    assert "play" in game.sections
    assert "score" in game.sections
    assert "quit_confirm" in game.popups
    assert "no_more_levels" in game.popups
    assert game.levels.get_level().title == "Boot"
    assert game.interface.score.get_width() > 0
