"""Reference reader and validator for VIDEO.md packages (spec: SPEC.md)."""
from __future__ import annotations

import json
import re
from importlib import resources
from pathlib import Path

import yaml

__version__ = "1.0.0"

FORMAT = "videomd"
VERSION = 1
ENTRY = "VIDEO.md"
DIR = "video"
BLOCK = "videomd-timeline"
TIME_TOLERANCE = 0.06  # seconds between a timeline line and its shot file

_RE_HEAD = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
_RE_LINE = re.compile(r"^#(\d+) (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)((?: \| [a-z][a-z0-9_-]*~? [^|]+?)*)$")
_RE_ID = re.compile(r"\(([a-z_0-9-]+)\)")
_RE_MAP_ROW = re.compile(r"^\| `([^`]+)` \|", re.M)


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


def timeline_block(body: str) -> list[str] | None:
    m = re.search(rf"```{BLOCK}\n(.*?)\n?```", body, re.S)
    return None if m is None else [x for x in m.group(1).split("\n") if x.strip()]


def shot_file(root: Path, n: int) -> Path:
    return Path(root) / DIR / "shots" / f"{n:02d}.md"


def read(root: Path) -> dict:
    """{"card": {...}, "timeline": [{"shot", "start", "end", <key>: <value>}], "shots": {n: front matter}}."""
    root = Path(root)
    card, _ = read_file(root / ENTRY)
    _, tl = read_file(root / DIR / "timeline.md")
    shots = {}
    for p in sorted((root / DIR / "shots").glob("*.md")):
        fm, _ = read_file(p)
        shots[fm.get("shot")] = fm
    rows = [x for x in map(parse_timeline_line, timeline_block(tl) or []) if x]
    return {"card": card, "timeline": rows, "shots": shots}


def _schema_errors(data: dict, part: str, where: str) -> list[str]:
    import jsonschema

    v = jsonschema.Draft202012Validator({**schema(), "$ref": f"#/$defs/{part}"})
    return [f"{where}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in v.iter_errors(data)]


def check(root: Path) -> list[str]:
    """Every rule in SPEC.md “Conformance” that `root` breaks; an empty list means it conforms."""
    root = Path(root)
    errs: list[str] = []
    entry = root / ENTRY
    if not entry.is_file():
        return [f"{ENTRY} missing"]
    card, body = read_file(entry)
    if not card:
        return [f"{ENTRY}: no front matter"]
    errs += _schema_errors(card, "card", ENTRY)
    for p in _RE_MAP_ROW.findall(body):
        if "…" not in p and "," not in p and not (root / p).exists():
            errs.append(f"{ENTRY}: map lists {p}, which does not exist")
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
    lines = timeline_block(tl)
    if lines is None:
        return errs + [f"{DIR}/timeline.md: no ```{BLOCK} block"]
    rows = []
    for ln in lines:
        if not _RE_LINE.match(ln):
            errs.append(f"{DIR}/timeline.md: not a timeline line: {ln[:80]}")
            continue
        rows.append(parse_timeline_line(ln))
    if card.get("shots") is not None and len(rows) != card["shots"]:
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
        made = _RE_ID.search(x.get("made~", ""))
        if made and made.group(1) != (fm.get("inferred") or {}).get("made"):
            errs.append(f"{rel}: inferred.made differs from the timeline's made~")
        for k, fp in (fm.get("frames") or {}).items():
            if not (root / str(fp)).is_file():
                errs.append(f"{rel}: frames.{k} {fp} does not exist")
    return errs
