# VIDEO.md

**An open format for video breakdowns that models read layer by layer.**

English · [中文](i18n/README_zh.md)

Every skill has a `SKILL.md`. Every video gets a `VIDEO.md`.

A `VIDEO.md` package describes one video: what it says, how each shot was made, what is on screen, what the sound is, and how to remake it. It starts with a card of about 150 tokens and opens up, level by level, down to a single shot. Every file says how many tokens it holds, and what was **seen** is always kept apart from what was **inferred**.

```
coffee-ad/
  VIDEO.md            the card (front matter) + overview and map
  video/
    timeline.md       one line per shot
    sound.md  …       one topic per file
    shots/01.md       everything about one shot
  frames/ …           raw data and media, as the producer likes
```

## At a glance

The card, at the top of `VIDEO.md`:

```yaml
---
videomd: 1
name: coffee-ad
description: Mixed — filmed 70% + code-rendered text card 30%
source: {file: coffee-ad.mp4, duration: 10.0, size: 1080x1920, fps: 30.0}
shots: 2
made_mix: {live_action: 0.7, code_render: 0.3}
readers: [tools, model]
lang: en
---
```

The timeline, one shot per line. A key ending in `~` is inferred; the others are seen or measured:

````
```videomd-timeline
#01 0.0-7.0 | seen hand pours coffee into a glass cup | cam handheld | made~ filmed(live_action) 92%
#02 7.0-10.0 | seen beige card with the price | cam static | over title | made~ code render(code_render) 61% · runner-up screen capture 30% | flag low confidence
```
````

## Why

A breakdown's raw data runs to hundreds of thousands of tokens. A model that reads it for every question is slow, costly, and tends to repeat guesses as facts. With VIDEO.md:

- **Most questions are answered from the card and the overview**, about 2k tokens. Adding the timeline, about 4k, covers questions about single shots.
- **The cost is known before reading.** Every file and every row of the map gives its size in tokens.
- **Seen and inferred are kept apart**, in the syntax (`made~`) and in the data (`inferred`, with a probability and `decided_by`).
- **Programs get a stable surface**: front matter with a JSON Schema, a one-line-per-shot grammar, fixed ids. Unknown fields, keys and files are ignored, so the format can grow.

More in [DESIGN.md](DESIGN.md): how it borrows from Agent Skills and small DSLs, and the reasons behind each decision.

## Documents

- [SPEC.md](SPEC.md): the specification, version 1
- [TAXONOMY.md](TAXONOMY.md): standard ids for production methods, camera, overlays, readers, flags
- [DESIGN.md](DESIGN.md): why it looks the way it does
- [schema/videomd-1.schema.json](schema/videomd-1.schema.json): JSON Schema for every front matter
- [examples/](examples/): complete packages
- [conformance/](conformance/): packages that conform, and packages that each break one rule
- [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md): tools that write or read VIDEO.md

## Check and read a package

```bash
pip install videomd
videomd check path/to/package      # lists every rule it breaks; exit code 1 if any
videomd read path/to/package       # card, timeline and shot data as JSON
```

```python
import videomd

errors = videomd.check("path/to/package")
pkg = videomd.read("path/to/package")   # {"card": {...}, "timeline": [...], "shots": {1: {...}}}
```

## For agents

Read `VIDEO.md` first; most questions stop there. Read `video/timeline.md` for questions about shots, and look for `flag`. Open `video/shots/<n>.md` and its `frames` only to check one shot. Open topic files from the map when the question is about that topic. Leave raw data to programs.

## Contributing

Proposals for new fields, keys or taxonomy ids are welcome as issues. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The specification and documents are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code, schema and conformance files are under [Apache-2.0](LICENSE).
