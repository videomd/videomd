"""Reference reader and validator for VIDEO.md packages (spec: SPEC.md)."""
from __future__ import annotations

import json
import re
from importlib import resources
from pathlib import Path

import yaml

__version__ = "1.2.0"

FORMAT = "videomd"
VERSION = 1
ENTRY = "VIDEO.md"
DIR = "video"
TIMELINE_BLOCK = "videomd-timeline"
MAP_BLOCK = "videomd-map"
SCENES_BLOCK = "videomd-scenes"
TIME_TOLERANCE = 0.06  # seconds between a timeline line and its shot file

# timeline keys defined by the spec, in line order; `~` = inferred
KEYS = ("story", "seen", "layers", "camera", "transition", "overlay", "made~", "material~", "remake", "flag")

_RE_HEAD = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
_RE_LINE = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)((?: \| [a-z][a-z0-9_-]*~? [^|]+?)*)$")
_RE_SCENE_HEAD = re.compile(r"^#S(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
_RE_SCENE_SHOTS = re.compile(r"^(\d+)-(\d+)$")
_RE_MAP = re.compile(r"^(\S+) \| (\d+|-) \| ([^|]+)$")


def schema() -> dict:
    return json.loads(resources.files(__package__).joinpath("videomd-1.schema.json").read_text(encoding="utf-8"))


def read_file(path: Path) -> tuple[dict, str]:
    """(front matter, body) of one file in a package."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    fm, _, body = text[4:].partition("\n---\n")
    data = yaml.safe_load(fm)
    return (data if isinstance(data, dict) else {}), body.strip()


def block(body: str, name: str) -> list[str] | None:
    """Non-empty lines of the fenced block with info string `name`; None if there is none."""
    m = re.search(rf"^```{re.escape(name)}[ \t]*\n(.*?)^```", body, re.S | re.M)
    return None if m is None else [x for x in m.group(1).split("\n") if x.strip()]


def parse_timeline_line(line: str) -> dict | None:
    """`#07 16.2-18.5 | seen … | made~ …` -> {"shot": 7, "start": 16.2, "end": 18.5, "seen": "…", "made~": "…"}; None if not a shot line."""
    parts = line.strip().split(" | ")
    m = _RE_HEAD.match(parts[0])
    if not m:
        return None
    out: dict = {"shot": int(m.group(1)), "start": float(m.group(2)), "end": float(m.group(3))}
    for p in parts[1:]:
        k, _, v = p.partition(" ")
        out[k] = v
    return out


def parse_map_line(line: str) -> dict | None:
    """`video/timeline.md | 2049 | One line per shot` -> {"path", "tokens" (int or None), "about"}; None if malformed."""
    m = _RE_MAP.match(line.strip())
    if not m:
        return None
    return {"path": m.group(1), "tokens": None if m.group(2) == "-" else int(m.group(2)), "about": m.group(3).strip()}


def parse_scene_line(line: str) -> dict | None:
    """`#S03 120.0-310.5 | shots 14-38 | story …` -> {"scene": 3, "start", "end", "shots": [14, 38], "story": "…"}; None if malformed."""
    parts = line.strip().split(" | ")
    m = _RE_SCENE_HEAD.match(parts[0])
    if not m:
        return None
    out: dict = {"scene": int(m.group(1)), "start": float(m.group(2)), "end": float(m.group(3))}
    for p in parts[1:]:
        k, _, v = p.partition(" ")
        if not k or not v:
            return None
        out[k] = v
    r = _RE_SCENE_SHOTS.match(out.get("shots", ""))
    if not r:
        return None
    out["shots"] = [int(r.group(1)), int(r.group(2))]
    return out


def timeline_files(root: Path) -> list[Path]:
    """The files that hold the timeline: video/timeline.md, or its parts under video/timeline/ when it is split."""
    root = Path(root)
    parts = sorted((root / DIR / "timeline").glob("*.md"))
    return parts or [root / DIR / "timeline.md"]


def shot_file(root: Path, n: int) -> Path:
    return Path(root) / DIR / "shots" / f"{n:02d}.md"


def read(root: Path) -> dict:
    """{"card", "map", "scenes": [scene lines], "timeline": [{"shot", "start", "end", <key>: <value>}], "shots": {n: front matter}}."""
    root = Path(root)
    card, body = read_file(root / ENTRY)
    lines: list[str] = []
    for f in timeline_files(root):
        if f.is_file():
            lines += block(read_file(f)[1], TIMELINE_BLOCK) or []
    scenes = []
    if (root / DIR / "scenes.md").is_file():
        scenes = [x for x in map(parse_scene_line, block(read_file(root / DIR / "scenes.md")[1], SCENES_BLOCK) or []) if x]
    shots = {}
    for p in sorted((root / DIR / "shots").glob("*.md")):
        fm, _ = read_file(p)
        shots[fm.get("shot")] = fm
    return {"card": card,
            "map": [x for x in map(parse_map_line, block(body, MAP_BLOCK) or []) if x],
            "scenes": scenes,
            "timeline": [x for x in map(parse_timeline_line, lines) if x],
            "shots": shots}


def _schema_errors(data: dict, part: str, where: str) -> list[str]:
    import jsonschema

    v = jsonschema.Draft202012Validator({**schema(), "$ref": f"#/$defs/{part}"})
    return [f"{where}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in v.iter_errors(data)]


def _safe(p: str) -> bool:
    return not p.startswith("/") and ".." not in Path(p).parts


def _map_errors(root: Path, body: str) -> list[str]:
    lines = block(body, MAP_BLOCK)
    if lines is None:
        return [f"{ENTRY}: no ```{MAP_BLOCK} block"]
    errs, listed = [], []
    for ln in lines:
        e = parse_map_line(ln)
        if e is None:
            errs.append(f"{ENTRY}: not a map line: {ln[:80]}")
            continue
        p = e["path"]
        if not _safe(p):
            errs.append(f"{ENTRY}: map path {p} is not relative to the package")
        elif any(c in p for c in "*?["):
            hits = list(root.glob(p))
            if not hits:
                errs.append(f"{ENTRY}: map pattern {p} matches nothing")
            listed += hits
        elif not (root / p).exists() or (p.endswith("/") and not (root / p).is_dir()):
            errs.append(f"{ENTRY}: map lists {p}, which does not exist")
        else:
            listed.append(root / p)
    listed_set = {q.resolve() for q in listed}
    for q in sorted((root / DIR).glob("*.md")) + sorted((root / DIR / "timeline").glob("*.md")):
        if q.resolve() not in listed_set:
            errs.append(f"{ENTRY}: map does not list {q.relative_to(root).as_posix()}")
    return errs


def check(root: Path) -> list[str]:
    """Every rule in SPEC.md “Conformance” that `root` breaks; an empty list means it conforms."""
    root = Path(root)
    entry = root / ENTRY
    if not entry.is_file():
        return [f"{ENTRY} missing"]
    card, body = read_file(entry)
    if not card:
        return [f"{ENTRY}: no front matter"]
    errs = _schema_errors(card, "card", ENTRY) + _map_errors(root, body)
    for p in sorted((root / DIR).glob("*.md")):
        fm, _ = read_file(p)
        if not fm:
            errs.append(f"{DIR}/{p.name}: no front matter")
            continue
        errs += _schema_errors(fm, "part", f"{DIR}/{p.name}")
    tl_path = root / DIR / "timeline.md"
    if not tl_path.is_file():
        return errs + [f"{DIR}/timeline.md missing"]
    _, tl = read_file(tl_path)
    parts = sorted((root / DIR / "timeline").glob("*.md"))
    lines: list[tuple[str, str]] = []
    own = block(tl, TIMELINE_BLOCK)
    if parts and own is not None:
        errs.append(f"{DIR}/timeline.md: has a ```{TIMELINE_BLOCK} block and parts under {DIR}/timeline/; use one or the other")
    if not parts:
        if own is None:
            return errs + [f"{DIR}/timeline.md: no ```{TIMELINE_BLOCK} block"]
        lines = [(f"{DIR}/timeline.md", ln) for ln in own]
    for q in parts:
        rel = f"{DIR}/timeline/{q.name}"
        fm, body_q = read_file(q)
        if not fm:
            errs.append(f"{rel}: no front matter")
            continue
        errs += _schema_errors(fm, "part", rel)
        if fm.get("part") != "timeline":
            errs.append(f"{rel}: part must be timeline")
        got = block(body_q, TIMELINE_BLOCK)
        if got is None:
            errs.append(f"{rel}: no ```{TIMELINE_BLOCK} block")
            continue
        lines += [(rel, ln) for ln in got]
    rows = []
    for where, ln in lines:
        if not _RE_LINE.match(ln):
            errs.append(f"{where}: not a timeline line: {ln[:80]}")
            continue
        rows.append(parse_timeline_line(ln))
    if isinstance(card.get("shots"), int) and len(rows) != card["shots"]:
        errs.append(f"{DIR}/timeline.md: {len(rows)} lines, card says {card['shots']} shots")
    last = 0
    shot_fm: dict[int, dict] = {}
    for x in rows:
        if x["shot"] <= last:
            errs.append(f"{DIR}/timeline.md: #{x['shot']:02d} out of order")
        if x["end"] < x["start"]:
            errs.append(f"{DIR}/timeline.md: #{x['shot']:02d} ends before it starts")
        last = x["shot"]
        sp = shot_file(root, x["shot"])
        rel = f"{DIR}/shots/{sp.name}"
        if not sp.is_file():
            errs.append(f"{rel} missing")
            continue
        fm, _ = read_file(sp)
        shot_fm[x["shot"]] = fm
        errs += _schema_errors(fm, "shot", rel)
        t = fm.get("time") if isinstance(fm.get("time"), list) and len(fm["time"]) == 2 else [None, None]
        if fm.get("shot") != x["shot"] or t[0] is None or abs(t[0] - x["start"]) > TIME_TOLERANCE or abs(t[1] - x["end"]) > TIME_TOLERANCE:
            errs.append(f"{rel}: shot number or time differs from the timeline")
        else:
            errs += _inside_shot(fm, x["start"], x["end"], rel)
        for k, fp in (fm.get("frames") or {}).items():
            if not (_safe(str(fp)) and (root / str(fp)).is_file()):
                errs.append(f"{rel}: frames.{k} {fp} does not exist")
    errs += _take_errors(rows, shot_fm)
    errs += _scene_errors(root, card, rows, shot_fm)
    errs += _track_errors(root, card)
    shot_numbers = {x["shot"] for x in rows}
    for q in sorted((root / DIR / "shots").glob("*.md")):
        fm, _ = read_file(q)
        if q.stem.isdigit() and fm.get("shot") != int(q.stem):
            errs.append(f"{DIR}/shots/{q.name}: file name and shot number differ")
        elif fm.get("shot") not in shot_numbers:
            errs.append(f"{DIR}/shots/{q.name}: no timeline line for this shot")
    return errs


def _within(t, start: float, end: float) -> bool:
    return isinstance(t, list) and len(t) == 2 and all(isinstance(v, (int, float)) for v in t) \
        and t[0] <= t[1] and t[0] >= start - TIME_TOLERANCE and t[1] <= end + TIME_TOLERANCE


def _inside_shot(fm: dict, start: float, end: float, rel: str) -> list[str]:
    """Beats and camera moves lie inside the shot; a transition into the shot spans its start; layer regions lie in the frame."""
    errs = []
    for i, b in enumerate(fm.get("beats") or []):
        if isinstance(b, dict) and "time" in b and not _within(b["time"], start, end):
            errs.append(f"{rel}: beats/{i} is outside the shot")
    cams = [fm.get("camera")] + [(l or {}).get("camera") for l in (fm.get("layers") or []) if isinstance(l, dict)]
    for cam in cams:
        if isinstance(cam, dict):
            for i, m in enumerate(cam.get("moves") or []):
                if isinstance(m, dict) and "time" in m and not _within(m["time"], start, end):
                    errs.append(f"{rel}: camera/moves/{i} is outside the shot")
    tr = fm.get("transition_in")
    if isinstance(tr, dict) and isinstance(tr.get("time"), list) and len(tr["time"]) == 2:
        a, b = tr["time"]
        if not (a <= start + TIME_TOLERANCE and b >= start - TIME_TOLERANCE):
            errs.append(f"{rel}: transition_in does not span the start of the shot")
    ids = []
    for i, l in enumerate(fm.get("layers") or []):
        if not isinstance(l, dict):
            continue
        ids.append(l.get("id"))
        r = l.get("region")
        if isinstance(r, list) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r) and (r[0] + r[2] > 1.0001 or r[1] + r[3] > 1.0001):
            errs.append(f"{rel}: layers/{i} region goes outside the frame")
    if len(ids) != len(set(ids)):
        errs.append(f"{rel}: layer ids repeat")
    return errs


def _take_errors(rows: list[dict], shot_fm: dict[int, dict]) -> list[str]:
    """Shots of one take follow each other without a gap."""
    errs, prev = [], None
    seen_takes: set[int] = set()
    for x in rows:
        take = (shot_fm.get(x["shot"]) or {}).get("take")
        if take is None:
            prev = None
            continue
        if prev and prev[0] == take:
            if abs(prev[1] - x["start"]) > TIME_TOLERANCE:
                errs.append(f"{DIR}/shots/{x['shot']:02d}.md: take {take} has a gap before this shot")
        elif take in seen_takes:
            errs.append(f"{DIR}/shots/{x['shot']:02d}.md: take {take} is not continuous")
        seen_takes.add(take)
        prev = (take, x["end"])
    return errs


def _scene_errors(root: Path, card: dict, rows: list[dict], shot_fm: dict[int, dict]) -> list[str]:
    path = root / DIR / "scenes.md"
    if not path.is_file():
        if isinstance(card.get("scenes"), int):
            return [f"{ENTRY}: card says {card['scenes']} scenes, but {DIR}/scenes.md is missing"]
        return []
    rel = f"{DIR}/scenes.md"
    fm, body = read_file(path)
    lines = block(body, SCENES_BLOCK)
    if lines is None:
        return [f"{rel}: no ```{SCENES_BLOCK} block"]
    errs, scenes = [], []
    for ln in lines:
        x = parse_scene_line(ln)
        if x is None:
            errs.append(f"{rel}: not a scene line: {ln[:80]}")
        else:
            scenes.append(x)
    for n, label in ((fm.get("scenes"), rel), (card.get("scenes"), ENTRY)):
        if isinstance(n, int) and n != len(scenes):
            errs.append(f"{label}: says {n} scenes, {rel} has {len(scenes)} lines")
    by_shot = {x["shot"]: x for x in rows}
    numbers = [x["shot"] for x in rows]
    expect, last = (numbers[0] if numbers else None), 0
    for sc in scenes:
        a, b = sc["shots"]
        tag = f"{rel}: #S{sc['scene']:02d}"
        if sc["scene"] <= last:
            errs.append(f"{tag} out of order")
        last = sc["scene"]
        if a > b or a not in by_shot or b not in by_shot:
            errs.append(f"{tag} names shots {a}-{b}, which are not in the timeline")
            continue
        if expect is not None and a != expect:
            errs.append(f"{tag} starts at shot {a}; scenes must cover the timeline in order without gaps or overlaps")
        nxt = [n for n in numbers if n > b]
        expect = nxt[0] if nxt else None
        if abs(by_shot[a]["start"] - sc["start"]) > TIME_TOLERANCE or abs(by_shot[b]["end"] - sc["end"]) > TIME_TOLERANCE:
            errs.append(f"{tag} times differ from its shots")
        for n in numbers:
            if a <= n <= b:
                s_of = (shot_fm.get(n) or {}).get("scene")
                if s_of is not None and s_of != sc["scene"]:
                    errs.append(f"{DIR}/shots/{n:02d}.md: scene {s_of}, but {rel} puts it in scene {sc['scene']}")
    if scenes and expect is not None:
        errs.append(f"{rel}: shots from {expect} on are in no scene")
    return errs


def _track_errors(root: Path, card: dict) -> list[str]:
    errs = []
    for k, p in (card.get("tracks") or {}).items():
        if not (isinstance(p, str) and _safe(p) and (root / p).is_file()):
            errs.append(f"{ENTRY}: tracks.{k} {p} does not exist")
        elif k == "transcript" and not (root / p).read_text(encoding="utf-8", errors="replace").lstrip("\ufeff").startswith("WEBVTT"):
            errs.append(f"{ENTRY}: tracks.transcript {p} is not a WebVTT file")
    return errs
