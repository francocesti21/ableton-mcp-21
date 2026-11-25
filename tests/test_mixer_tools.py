"""Tests for the 21 Academy mixer additions (colors, routing, volume, pan,
mute, solo, overview and the configure_tracks batch).

Live's object model is faked with small Python classes; the Remote Script is
loaded the same way as in test_remote_script_bridge.py (no Ableton needed).
"""

import math

import pytest

from tests.test_remote_script_bridge import _load_script_module


class FakeParam(object):
    """Mimics a Live DeviceParameter. The volume curve maps 0.85 -> 0 dB."""

    def __init__(self, value, lo=0.0, hi=1.0, kind="volume"):
        self.value, self.min, self.max, self.kind = value, lo, hi, kind

    def str_for_value(self, v):
        if self.kind != "volume":
            return str(v)
        if v <= 0.0:
            return "-inf dB"
        # Monotonic stand-in for Live's fader law: 0.85 -> 0 dB, 1.0 -> +6 dB
        db = 40.0 * math.log10(v / 0.85) if v < 0.85 else (v - 0.85) / 0.15 * 6.0
        return "%.1f dB" % db


class FakeMixer(object):
    def __init__(self):
        self.volume = FakeParam(0.85)
        self.panning = FakeParam(0.0, -1.0, 1.0, kind="pan")


class FakeRouting(object):
    def __init__(self, name):
        self.display_name = name


class FakeTrack(object):
    def __init__(self, name, routes=("Main",), group=None, foldable=False):
        self.name = name
        self.color = 0x333333
        self.mute = False
        self.solo = False
        self.mixer_device = FakeMixer()
        self.available_output_routing_types = [FakeRouting(r) for r in routes]
        self.output_routing_type = self.available_output_routing_types[0]
        self.group_track = group
        self.is_grouped = group is not None
        self.is_foldable = foldable


class FakeSong(object):
    def __init__(self):
        drums = FakeTrack("DRUMS", routes=("Main", "BEAT", "Sends Only"), foldable=True)
        self.tracks = [
            drums,
            FakeTrack("Audio 1", routes=("Group", "Main", "BEAT", "BEAT FX"), group=drums),
            FakeTrack("Audio 2", routes=("Main", "DRUMS")),
        ]
        self.return_tracks = [FakeTrack("A Reverb")]
        self.master_track = FakeTrack("Main")


@pytest.fixture
def script():
    module = _load_script_module(fresh=True)
    inst = module.AbletonMCP.__new__(module.AbletonMCP)
    inst._song = FakeSong()
    inst.log_message = lambda *a, **k: None
    return inst


def test_color_names_hex_and_spanish(script):
    assert script._set_track_color(2, "#FF0000")["color"] == "#FF0000"
    assert script._set_track_color(2, "azul")["color"] == "#1E88E5"
    assert script._set_track_color(0, "red", "track")["color"] == "#E53935"
    with pytest.raises(ValueError):
        script._set_track_color(2, "not-a-color")


def test_volume_db_bisection_hits_target(script):
    r = script._set_track_volume(2, volume_db=-6.0)
    assert r["volume"] in ("-6.0 dB", "-5.9 dB", "-6.1 dB")
    r = script._set_track_volume(2, volume_db=0)
    assert r["volume"] in ("0.0 dB", "-0.0 dB", "0.1 dB", "-0.1 dB")
    r = script._set_track_volume(2, volume_db=12)   # above max -> clamps to max
    assert r["value"] == 1.0


def test_pan_is_clamped(script):
    assert script._set_track_pan(2, 5)["pan"] == 1.0
    assert script._set_track_pan(2, -0.25)["pan"] == -0.25


def test_mute_solo_and_return_tracks(script):
    assert script._set_track_mute(0, "x")["mute"] is True
    assert script._set_track_solo(0, False)["solo"] is False
    assert script._set_track_mute(0, True, "return")["name"] == "A Reverb"


def test_routing_exact_partial_ambiguous_and_missing(script):
    assert script._set_track_output_routing(2, "drums")["output"] == "DRUMS"
    assert script._set_track_output_routing(1, "group")["output"] == "Group"
    with pytest.raises(ValueError) as amb:
        script._set_track_output_routing(1, "bea")
    assert "ambiguous" in str(amb.value)
    with pytest.raises(ValueError) as missing:
        script._set_track_output_routing(2, "VOCES")
    assert "Options" in str(missing.value)


def test_index_out_of_range(script):
    with pytest.raises(IndexError):
        script._set_track_color(99, "red")


def test_overview_shape(script):
    o = script._get_tracks_overview()
    assert [t["name"] for t in o["tracks"]] == ["DRUMS", "Audio 1", "Audio 2"]
    assert o["tracks"][0]["is_group"] is True
    assert o["tracks"][1]["group"] == "DRUMS"
    assert o["tracks"][2]["output"] == "Main"
    assert o["returns"][0]["name"] == "A Reverb"
    assert o["master"]["name"] == "Main"


def test_configure_tracks_batch_continues_after_error(script):
    r = script._configure_tracks([
        {"track_index": 2, "name": "Kick", "color": "rojo", "output": "DRUMS",
         "volume_db": -6, "pan": 0.1, "mute": False},
        {"track_index": 50, "name": "nope"},
        {"track_index": 0, "track_type": "return", "color": "verde"},
    ])
    assert r["ok_count"] == 2 and r["error_count"] == 1
    t = script._song.tracks[2]
    assert t.name == "Kick" and t.output_routing_type.display_name == "DRUMS"
    assert t.color == 0xE53935
    assert script._song.return_tracks[0].color == 0x43A047


def test_capabilities_and_version_advertised():
    module = _load_script_module(fresh=True)
    for cap in ("configure_tracks", "set_track_output_routing", "get_tracks_overview",
                "set_track_color", "set_track_volume"):
        assert cap in module.SCRIPT_CAPABILITIES
    from MCP_Server.remote_script_install import EXPECTED_REMOTE_SCRIPT_VERSION
    assert module.SCRIPT_VERSION == EXPECTED_REMOTE_SCRIPT_VERSION


def test_create_delete_and_monitor(script):
    song = script._song
    song.create_audio_track = lambda i: song.tracks.append(FakeTrack("new"))
    song.create_midi_track = lambda i: song.tracks.append(FakeTrack("midi"))
    song.delete_track = lambda i: song.tracks.pop(i)
    r = script._create_tracks(4, "audio")
    assert r == {"created": 4, "kind": "audio", "first_index": 3, "last_index": 6}
    script._delete_tracks([3, 5], "track")
    assert len(song.tracks) == 5
    song.tracks[0].current_monitoring_state = 1
    out = script._configure_tracks([{"track_index": 0, "monitor": "in"}])
    assert song.tracks[0].current_monitoring_state == 0
    with pytest.raises(ValueError):
        script._set_track_monitoring(0, "loud")
