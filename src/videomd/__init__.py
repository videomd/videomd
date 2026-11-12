"""Reference reader and validator for VIDEO.md packages (spec: SPEC.md)."""
from __future__ import annotations

import json
import re
from importlib import resources
from pathlib import Path

import yaml

__version__ = "1.1.0"

FORMAT = "videomd"
VERSION = 1
ENTRY = "VIDEO.md"
DIR = "video"
TIMELINE_BLOCK = "videomd-timeline"
MAP_BLOCK = "videomd-map"
TIME_TOLERANCE = 0.06  # seconds between a timeline line and its shot file

# timeline keys defined by the spec, in line order; `~` = inferred
KEYS = ("story", "seen", "camera", "overlay", "made~", "material~", "remake", "flag")

_RE_HEAD = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
_RE_LINE = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)((?: \| [a-z][a-z0-9_-]*~? [^|]+?)*)$")
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


def shot_file(root: Path, n: int) -> Path:
    return Path(root) / DIR / "shots" / f"{n:02d}.md"


def read(root: Path) -> dict:
    """{"card", "map": [entries], "timeline": [{"shot", "start", "end", <key>: <value>}], "shots": {n: front matter}}."""
    root = Path(root)
    card, body = read_file(root / ENTRY)
    _, tl = read_file(root / DIR / "timeline.md")
    shots = {}
    for p in sorted((root / DIR / "shots").glob("*.md")):
        fm, _ = read_file(p)
        shots[fm.get("shot")] = fm
    return {"card": card,
            "map": [x for x in map(parse_map_line, block(body, MAP_BLOCK) or []) if x],
            "timeline": [x for x in map(parse_timeline_line, block(tl, TIMELINE_BLOCK) or []) if x],
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
    for q in sorted((root / DIR).glob("*.md")):
        if q.resolve() not in listed_set:
            errs.append(f"{ENTRY}: map does not list {DIR}/{q.name}")
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
    lines = block(tl, TIMELINE_BLOCK)
    if lines is None:
        return errs + [f"{DIR}/timeline.md: no ```{TIMELINE_BLOCK} block"]
    rows = []
    for ln in lines:
        if not _RE_LINE.match(ln):
            errs.append(f"{DIR}/timeline.md: not a timeline line: {ln[:80]}")
            continue
        rows.append(parse_timeline_line(ln))
    if isinstance(card.get("shots"), int) and len(rows) != card["shots"]:
        errs.append(f"{DIR}/timeline.md: {len(rows)} lines, card says {card['shots']} shots")
    last = 0
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
        errs += _schema_errors(fm, "shot", rel)
        t = fm.get("time") if isinstance(fm.get("time"), list) and len(fm["time"]) == 2 else [None, None]
        if fm.get("shot") != x["shot"] or t[0] is None or abs(t[0] - x["start"]) > TIME_TOLERANCE or abs(t[1] - x["end"]) > TIME_TOLERANCE:
            errs.append(f"{rel}: shot number or time differs from the timeline")
        for k, fp in (fm.get("frames") or {}).items():
            if not (_safe(str(fp)) and (root / str(fp)).is_file()):
                errs.append(f"{rel}: frames.{k} {fp} does not exist")
    shot_numbers = {x["shot"] for x in rows}
    for q in sorted((root / DIR / "shots").glob("*.md")):
        fm, _ = read_file(q)
        if q.stem.isdigit() and fm.get("shot") != int(q.stem):
            errs.append(f"{DIR}/shots/{q.name}: file name and shot number differ")
        elif fm.get("shot") not in shot_numbers:
            errs.append(f"{DIR}/shots/{q.name}: no timeline line for this shot")
    return errs
