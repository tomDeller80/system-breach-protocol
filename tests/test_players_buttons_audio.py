from types import SimpleNamespace

import pygame as pg

from buttons import Button
from mixer import AudioManager
from players import Player, Players
from core import Storage


def test_players_load_save_and_update(monkeypatch):
    saved = {}

    sample = {
        "players": {
            "1": {
                "name": "ALPHA",
                "level": "One",
                "lives": 3,
                "score": 100,
                "power_ups": [],
                "created_at": "2026-01-01T00:00:00",
                "last_played": "2026-01-01T00:00:00",
            }
        }
    }

    monkeypatch.setattr(Storage, "read_json", staticmethod(lambda *args, **kwargs: sample))
    monkeypatch.setattr(Storage, "write_json", staticmethod(lambda json_file, data: saved.update(data)))

    players = Players()
    assert len(players.players) == 1
    assert players.players[0].name == "ALPHA"

    players.set_player("ALPHA")
    assert players.get_player().name == "ALPHA"

    players.update_player(score=250)
    assert players.get_player().score == 250
    assert saved["players"]["1"]["score"] == 250

    new_profile = players.add_player({"name": "BETA", "level": "Two", "lives": 2, "score": 50})
    assert isinstance(new_profile, Player)
    assert new_profile.name == "BETA"


def test_button_hover_and_click(asset_stubs, monkeypatch):
    clicks = []
    game = SimpleNamespace(audio_manager=SimpleNamespace(play_sfx=lambda *args, **kwargs: None))

    button = Button(
        game=game,
        assets=["start.png", "start_hover.png"],
        pos=(20, 20),
        callback=lambda: clicks.append(True),
        scale=1,
    )

    button.handle_event(pg.event.Event(pg.MOUSEMOTION, {"pos": button.rect.center}))
    assert button.is_hovered is True

    button.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": button.rect.center}))
    assert clicks == [True]


def test_audio_manager_loads_and_plays(asset_stubs, monkeypatch):
    calls = []

    monkeypatch.setattr(pg.mixer.music, "load", lambda path: calls.append(("load", path)))
    monkeypatch.setattr(pg.mixer.music, "play", lambda loops, fade_ms=0: calls.append(("play", loops, fade_ms)))
    monkeypatch.setattr(pg.mixer.music, "pause", lambda: calls.append(("pause",)))
    monkeypatch.setattr(pg.mixer.music, "unpause", lambda: calls.append(("unpause",)))
    monkeypatch.setattr(pg.mixer.music, "stop", lambda: calls.append(("stop",)))
    monkeypatch.setattr(pg.mixer.music, "fadeout", lambda time: calls.append(("fadeout", time)))
    monkeypatch.setattr(pg.mixer.music, "get_volume", lambda: 0.75)
    monkeypatch.setattr(pg.mixer.music, "set_volume", lambda volume: calls.append(("volume", volume)))

    audio = AudioManager()
    assert "hit-block" in audio.sounds
    assert "synthwav" in audio.music_tracks

    audio.play_music("synthwav")
    audio.pause_music()
    audio.unpause_music()
    audio.stop_music()
    audio.fadeout_music(250)
    audio.set_music_volume(0.5)
    audio.play_sfx("click")

    assert ("play", -1, 2000) in calls
    assert ("pause",) in calls
    assert ("unpause",) in calls
    assert ("stop",) in calls
    assert ("fadeout", 250) in calls
    assert ("volume", 0.5) in calls
