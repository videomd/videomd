"""Every valid case and the example conform; every invalid case fails with the error named in its EXPECT file."""
import json
from pathlib import Path

import pytest

import videomd

ROOT = Path(__file__).resolve().parents[1]
VALID = [p for p in sorted((ROOT / "conformance" / "valid").iterdir()) + sorted((ROOT / "examples").iterdir()) if p.is_dir()]
INVALID = [p for p in sorted((ROOT / "conformance" / "invalid").iterdir()) if p.is_dir()]


@pytest.mark.parametrize("d", VALID, ids=lambda p: p.name)
def test_valid(d):
    assert videomd.check(d) == []


@pytest.mark.parametrize("d", INVALID, ids=lambda p: p.name)
def test_invalid(d):
    want = (d / "EXPECT").read_text(encoding="utf-8").strip()
    errs = videomd.check(d)
    assert errs and any(want in e for e in errs), errs


def test_schema_copies_match():
    a = json.loads((ROOT / "schema" / "videomd-1.schema.json").read_text(encoding="utf-8"))
    assert a == videomd.schema()


def test_read_gives_card_timeline_and_shots():
    pkg = videomd.read(ROOT / "conformance" / "valid" / "minimal")
    assert pkg["card"]["shots"] == 2 == len(pkg["timeline"]) == len(pkg["shots"])
    assert [x["path"] for x in pkg["map"]] == ["video/timeline.md", "video/shots/*.md"]
    assert pkg["timeline"][1] == {"shot": 2, "start": 5.0, "end": 8.0, "seen": "a shopfront with warm lights"}
    assert "inferred" not in pkg["shots"][2]   # the production-method module is optional
    full = videomd.read(ROOT / "conformance" / "valid" / "full")
    assert full["shots"][2]["inferred"]["made"] == "x-game_capture" and full["map"][-1] == {"path": "frames/", "tokens": None, "about": "Shot frames · checking by eye"}


def test_timeline_line_grammar():
    assert videomd.parse_timeline_line("#07 16.2-18.5 | seen red ring | made~ screen capture(screen_capture) 44%") == {
        "shot": 7, "start": 16.2, "end": 18.5, "seen": "red ring", "made~": "screen capture(screen_capture) 44%"}
    assert videomd.parse_timeline_line("## heading") is None
    assert videomd.parse_map_line("video/shots/*.md | 570 | Per-shot detail") == {"path": "video/shots/*.md", "tokens": 570, "about": "Per-shot detail"}
    assert videomd.parse_map_line("video/sound.md 956 Sound") is None


def test_long_film_reads_scenes_and_a_split_timeline():
    pkg = videomd.read(ROOT / "conformance" / "valid" / "long-film")
    assert [s["shots"] for s in pkg["scenes"]] == [[1, 4], [5, 6]]
    assert [x["shot"] for x in pkg["timeline"]] == [1, 2, 3, 4, 5, 6]
    assert pkg["shots"][5]["take"] == pkg["shots"][6]["take"] == 1
    assert pkg["card"]["tracks"]["transcript"] == "video/transcript.vtt"


def test_composite_layers_and_camera_moves():
    pkg = videomd.read(ROOT / "conformance" / "valid" / "composite")
    layers = pkg["shots"][1]["layers"]
    assert [l["id"] for l in layers] == ["trailer", "webcam"] and layers[1]["made"] == "live_action"
    assert [m["type"] for m in pkg["shots"][2]["camera"]["moves"]] == ["orbit", "whip_pan"]
    assert pkg["shots"][3]["transition_in"]["type"] == "whip"


def test_scene_line_grammar():
    assert videomd.parse_scene_line("#S03 120.0-310.5 | shots 14-38 | story the chase") == {
        "scene": 3, "start": 120.0, "end": 310.5, "shots": [14, 38], "story": "the chase"}
    assert videomd.parse_scene_line("#S03 120.0-310.5 | story no shots") is None
