# VIDEO.md

**An open format for video breakdowns that models read layer by layer.**

**[videomd.github.io/videomd](https://videomd.github.io/videomd/)** · English · [中文](i18n/README_zh.md)

Every skill has a `SKILL.md`. Every video gets a `VIDEO.md`.

A VIDEO.md package describes one video for AI agents and programs: what it shows and says, shot by shot, and, when the producer knows, how each shot was made and how to remake it. It starts with a small card and opens up level by level, down to a single shot. Every file says how many tokens it holds, and what was **seen** is kept apart from what was **inferred**.

> **Status:** version 1, draft. The format may still change before it is marked final; see [CHANGELOG.md](CHANGELOG.md).

## What a package looks like

```
coffee-ad/
  VIDEO.md            the card + overview and map          read first
  video/
    timeline.md       one line per shot                    read for questions about shots
    sound.md  …       one topic per file                   read when the question is about it
    shots/01.md       everything about one shot            read to check a shot
  frames/ …           raw data and media                   for programs and image models
```

The card, at the top of `VIDEO.md`, is all an agent needs to decide whether to open the package:

```yaml
---
videomd: 1
name: coffee-ad
description: >-
  A 10-second coffee ad: a hand pours coffee into a glass, then a card shows the price.
  Filmed product shot (70%) followed by a code-rendered price card (30%).
source: {file: coffee-ad.mp4, sha256: 9f86d0…, duration: 10.0}
shots: 2
lang: en
---
```

The timeline has one line per shot. A key ending in `~` is inferred; the others are seen or measured:

```
#01 0.0-7.0 | seen hand pours coffee into a glass cup | camera handheld | made~ filmed 92%
#02 7.0-10.0 | seen beige card with the price | overlay title | made~ code render 61% · runner-up screen capture 30% | flag low confidence
```

## Why

A full breakdown of one video runs to hundreds of thousands of tokens. A model that reads it for every question is slow, costly, and tends to repeat guesses as facts. With VIDEO.md:

- **An agent can know about many videos at once.** Keep each card in context, a few hundred tokens apiece, and open a package only when it is needed, as with skills.
- **Most questions are answered from the overview**, about 2k tokens. With the timeline, about 4k, questions about single shots are answered too.
- **The cost is known before reading.** The map lists every file with its size in tokens.
- **Seen and inferred are kept apart**, in the syntax (`made~`) and in the data (`inferred`, with a probability and who decided).
- **Programs get a stable surface**: front matter checked by a JSON Schema, a one-line-per-shot grammar, fixed ids. Unknown fields, keys and files are ignored, so the format can grow.
- **It starts small.** Six fields make a valid card. Judging how a video was made is an optional module, not a requirement.

## Documents

| | |
|---|---|
| [SPEC.md](SPEC.md) | The specification |
| [docs/integrate.md](docs/integrate.md) | Using packages in an agent or app: discovery, context, loading, honest answers |
| [docs/authoring.md](docs/authoring.md) | Writing packages: from the smallest valid one to a full one |
| [docs/design.md](docs/design.md) | Why it looks the way it does: what it borrows from Agent Skills and small DSLs |
| [TAXONOMY.md](TAXONOMY.md) | Standard ids: production methods, camera, overlays, readers, flags |
| [schema/](schema/videomd-1.schema.json) | JSON Schema for every front matter |
| [examples/](https://github.com/videomd/videomd/tree/main/examples/) | Complete packages |
| [conformance/](https://github.com/videomd/videomd/tree/main/conformance/) | Packages that conform, and packages that each break one rule |
| [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md) | Tools that write or read VIDEO.md |

## Check and read a package

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

## Contributing

Proposals for fields, keys and taxonomy ids are welcome as issues; see [CONTRIBUTING.md](CONTRIBUTING.md). If you build a tool that writes or reads VIDEO.md, add it to [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md).

## License

The specification and documents are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code, schema and conformance files are under [Apache-2.0](https://github.com/videomd/videomd/blob/main/LICENSE).
