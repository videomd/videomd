<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="VIDEO.md" width="300">
</picture>

### An open format for video breakdowns that models read layer by layer

**Every skill has a `SKILL.md`. Every video gets a `VIDEO.md`.**

[![PyPI](https://img.shields.io/pypi/v/videomd?color=3d4fd6&label=pypi)](https://pypi.org/project/videomd/)
[![Spec](https://img.shields.io/badge/spec-version%201-3d4fd6)](docs/spec.md)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0%20%2B%20Apache--2.0-6e737d)](#license)

[**Website**](https://videomd.github.io/videomd/) · [Specification](docs/spec.md) · [Integrate](docs/integrate.md) · [Authoring](docs/authoring.md) · [中文](README.zh-CN.md)

</div>

---

A VIDEO.md package describes one video for AI agents and programs: what it shows and says, shot by shot, and, when the producer knows, how each shot was made and how to remake it. It starts with a small card and opens up level by level, down to a single shot. Every file says how many tokens it holds, and what was **seen** is kept apart from what was **inferred**.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/levels-dark.svg">
  <img src="docs/assets/levels-light.svg" alt="Levels of a VIDEO.md package: L0 card, L1 overview and map, L2 timeline and topics, L3 one shot, L4 raw data" width="100%">
</picture>

## At a glance

```
coffee-ad/
├── VIDEO.md            the card + overview and map      read first
├── video/
│   ├── timeline.md     one line per shot                read for questions about shots
│   ├── sound.md  …     one topic per file               read when the question is about it
│   └── shots/01.md     everything about one shot        read to check a shot
└── frames/ …           raw data and media               for programs and image models
```

<table>
<tr>
<td width="50%" valign="top">

**The card** — all an agent needs to decide whether to open the package

```yaml
---
videomd: 1
name: coffee-ad
description: >-
  A 10-second coffee ad: a hand pours
  coffee into a glass, then a card shows
  the price. Filmed (70%) + code-rendered
  price card (30%).
source:
  file: coffee-ad.mp4
  sha256: 9f86d0…
  duration: 10.0
shots: 2
lang: en
---
```

</td>
<td width="50%" valign="top">

**The timeline** — one line per shot; a key ending in `~` is inferred

```
#01 0.0-7.0
  | seen hand pours coffee into a glass
  | camera handheld
  | made~ filmed 92%

#02 7.0-10.0
  | seen beige card with the price
  | overlay title
  | made~ code render 61%
    · runner-up screen capture 30%
  | flag low confidence
```

</td>
</tr>
</table>

## Why VIDEO.md

A full breakdown of one video runs to hundreds of thousands of tokens. A model that reads it for every question is slow, costly, and tends to repeat guesses as facts.

| | |
|---|---|
| 🗂️ **Many videos in context** | Keep each card in context, a few hundred tokens apiece, and open a package only when it is needed, as with skills. |
| 🪜 **Read only what the question needs** | Most questions are answered from the overview, about 2k tokens; with the timeline, about 4k, questions about single shots too. |
| 🏷️ **Cost before reading** | The map lists every file with its size in tokens. |
| 🔍 **Seen apart from inferred** | In the syntax (`made~`) and in the data (`inferred`, with a probability and who decided). |
| 🧩 **A stable surface for programs** | Front matter checked by a JSON Schema, a one-line-per-shot grammar, fixed ids. Unknown fields, keys and files are ignored, so the format can grow. |
| 🎬 **From a 6-second ad to a feature film** | Scenes and a split timeline for long videos, takes and beats for one-take streams, layers for split screens and reactions, camera moves and transitions for whip pans, orbits and match cuts. All optional. |
| 🌱 **Starts small** | Six fields make a valid card. Judging how a video was made is an optional module, not a requirement. |

## Quick start

```bash
pip install videomd
videomd check path/to/package      # lists every rule it breaks; exit code 1 if any
videomd read path/to/package       # card, map, timeline and shot data as JSON
```

```python
import videomd

errors = videomd.check("path/to/package")
pkg = videomd.read("path/to/package")   # {"card": {...}, "map": [...], "timeline": [...], "shots": {1: {...}}}
```

- **Building an agent or app?** Read [docs/integrate.md](docs/integrate.md): discovery, what to put in context, when to load more, honest answers.
- **Building a breakdown tool?** Read [docs/authoring.md](docs/authoring.md): from the smallest valid package to a full one.
- **Want to see one?** Open [examples/salted-egg/VIDEO.md](https://github.com/videomd/videomd/blob/main/examples/salted-egg/VIDEO.md), a real 21-shot package.

## Documents

| | |
|---|---|
| [docs/spec.md](docs/spec.md) | The specification |
| [docs/integrate.md](docs/integrate.md) | Using packages in an agent or app |
| [docs/authoring.md](docs/authoring.md) | Writing packages |
| [docs/design.md](docs/design.md) | Why it looks the way it does: what it borrows from Agent Skills and small DSLs |
| [docs/taxonomy.md](docs/taxonomy.md) | Standard ids: production methods, camera, overlays, readers, flags |
| [schema/](schema/videomd-1.schema.json) | JSON Schema for every front matter |
| [examples/](https://github.com/videomd/videomd/tree/main/examples/) | Complete packages |
| [conformance/](https://github.com/videomd/videomd/tree/main/conformance/) | Packages that conform, and packages that each break one rule |
| [docs/implementations.md](docs/implementations.md) | Tools that write or read VIDEO.md |
| [CHANGELOG.md](CHANGELOG.md) | Changes by version |

## Implementations

| Tool | Role |
|---|---|
| [rea-video](https://github.com/JuneYaooo/rea-video) | Writes packages: shot-level breakdown, production method per shot, sound, packaging, remake plan |
| [videomd](https://github.com/videomd/videomd/tree/main/src/videomd/) | Reference reader and validator in this repository |

Built something that writes or reads VIDEO.md? Add it to [docs/implementations.md](docs/implementations.md).

## Contributing

Proposals for fields, keys and taxonomy ids are welcome as issues; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The specification and documents are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code, schema and conformance files are under [Apache-2.0](https://github.com/videomd/videomd/blob/main/LICENSE).
