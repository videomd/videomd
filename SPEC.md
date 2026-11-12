# VIDEO.md specification

This document defines the VIDEO.md package: a directory that describes one video for models and programs. For what it is and why, read the [README](README.md) and [docs/design.md](docs/design.md). For how to write one, [docs/authoring.md](docs/authoring.md); for how to use one in an agent or app, [docs/integrate.md](docs/integrate.md).

The key words MUST, MUST NOT, SHOULD and MAY are used as in RFC 2119.

## 1. Levels

A package is read in levels, each more detailed and more expensive than the one before:

| Level | Where | Typical size | Answers |
|---|---|---|---|
| L0 card | `VIDEO.md` front matter | 100–300 tokens | What the video is about and whether to open it |
| L1 overview and map | `VIDEO.md` body | 1–2k tokens | The verdict, the open questions, which file to open next |
| L2 topics | `video/<topic>.md` | hundreds to thousands | One aspect in full; `video/timeline.md` has one line per shot |
| L3 shots | `video/shots/<n>.md` | hundreds each | One shot in full |
| L4 raw | anything else in the directory | any | Data and media for programs, defined by the producer |

A reader SHOULD start at L0 and open the next level only when the question needs it.

## 2. Layout

```
<package>/
  VIDEO.md             required   L0 card + L1 overview and map
  video/
    timeline.md        required   L2 one line per shot
    content.md         optional   L2 what the video says, structure, script
    cast.md            optional   L2 characters, scenes, props
    sound.md           optional   L2 voice, music, sound effects, beats
    look.md            optional   L2 framing, camera, lighting, editing of filmed shots
    packaging.md       optional   L2 subtitles, styled text, stickers, picture-in-picture
    remake.md          optional   L2 how to remake the video
    x-<name>.md        optional   L2 producer-defined topics
    shots/01.md        required   L3 one file per shot
  ...                  optional   L4 producer-defined: raw data, frames, audio stems, subtitle files
```

- Paths in a package, including paths written inside its files, MUST be relative to the package root and MUST NOT start with `/` or contain a `..` segment.
- A producer SHOULD NOT write a topic file with nothing in it.
- Shot files are named by shot number, zero-padded to at least two digits: `01.md`, `02.md`, … `120.md`.

## 3. Front matter

Every `.md` file in a package MUST start with YAML front matter between two lines of `---`, and every front matter MUST contain the format version:

```yaml
videomd: 1
```

Files under `video/` MUST also contain `part` (which part this is) and `tokens` (the approximate size of the body):

```yaml
part: timeline
tokens: 2275
```

`part` is `timeline`, `content`, `cast`, `sound`, `look`, `packaging`, `remake`, `shot`, or `x-<name>`. `tokens` is an estimate so a reader can decide before opening the file; producers MAY use any tokenizer. One that needs none: ASCII characters ÷ 4 + other characters × 0.75.

The fields of each kind of front matter are defined by [schema/videomd-1.schema.json](schema/videomd-1.schema.json) (JSON Schema 2020-12): `card` for `VIDEO.md`, `part` for topic files, `shot` for shot files. Front matter MAY carry fields the schema does not define.

## 4. The card (L0)

The front matter of `VIDEO.md`. A minimal card:

```yaml
---
videomd: 1
name: city-walk
description: A two-shot city walk at dusk, from a crossing to a lit shopfront.
source: {file: city-walk.mp4, duration: 8.0}
shots: 2
lang: en
---
```

A card with every field:

```yaml
---
videomd: 1
name: coffee-ad
description: >-
  A 10-second coffee ad: a hand pours coffee into a glass, then a card shows the price.
  Filmed product shot (70%) followed by a code-rendered price card (30%).
source:
  file: coffee-ad.mp4
  url: https://example.com/videos/coffee-ad
  sha256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
  duration: 10.0
  size: 1080x1920
  fps: 30.0
  aspect: '9:16'
shots: 2
lang: en
made_mix: {live_action: 0.7, code_render: 0.3}
confidence: 0.84
readers: [tools, model]
open_questions: 1
generator: {name: rea-video, version: 0.1.0}
---
```

| Field | Required | Meaning |
|---|---|---|
| `videomd` | yes | Format version: `1` |
| `name` | yes | 1–64 characters: lowercase letters, digits and hyphens; no leading, trailing or double hyphen |
| `description` | yes | 1–1024 characters. What the video is about, then how it was made. See below |
| `source` | yes | `duration` in seconds, and at least one of `file` or `url` |
| `source.sha256` | no | Hex SHA-256 of the whole source file. Identifies the video across packages and producers |
| `source.size`, `fps`, `aspect` | no | `WxH`, frames per second, aspect ratio such as `'9:16'` |
| `shots` | yes | Number of shots; equals the number of timeline lines |
| `lang` | yes | Language of the text written for models (BCP 47), e.g. `en`, `zh`, `pt-BR` |
| `made_mix` | no | Production-method ids ([TAXONOMY.md](TAXONOMY.md)) to their share of the duration |
| `confidence` | no | 0–1, how sure the verdicts are overall |
| `readers` | no | Who took part in the verdicts: `tools`, `model`, `agent`, `human` |
| `open_questions` | no | Number of points that need a second look |
| `generator` | no | `name` and `version` of the producer |

**The description** is what an agent reads to decide whether this package answers a question, often among many packages, without opening anything else. It SHOULD say first what the video shows or says, and then, if known, how it was made. It SHOULD be specific enough to tell this video apart from similar ones.

Good: `A 66-second 3D plush-animal explainer on why salted duck eggs ooze oil, in four steps. Fully 3D rendered, with subtitles and stock music.`
Poor: `3D render 100%` (says how, not what) or `A video` (says nothing).

## 5. The overview and the map (L1)

The body of `VIDEO.md` is Markdown written for models. It SHOULD contain, in this order: what the video says and the verdict, the open questions, the map, and a short note on how to read the package.

The map MUST be a fenced code block with the info string `videomd-map`. Each line lists one path:

````
```videomd-map
video/timeline.md | 2078 | Timeline: one line per shot · which shot does what, which need a look
video/sound.md | 956 | Sound · voice, music, effects and beats
video/shots/*.md | 570 | Per-shot detail, tokens per file · checking one shot
breakdown.json | 75712 | Full raw data · for programs
shots/ | - | Frames · checking by eye
```
````

```
line   = path " | " tokens " | " about
path   = a file, a directory ending in "/", or a glob pattern (*, ?, [...])
tokens = an integer, or "-" for media and other files a model does not read as text
about  = what is in it, and when to read it; no "|"
```

- Every path that is not a pattern MUST exist; a directory path MUST be a directory. Every pattern MUST match at least one file. For a pattern, `tokens` is per file.
- Every `.md` file directly under `video/` MUST be covered by the map.
- Producers SHOULD list the L4 data they include, so a reader knows it is there.

## 6. Seen and inferred

A package keeps two kinds of statements apart:

- **Seen**: what is visible or audible and can be checked against the frames (what is on screen, camera movement, overlays, text), and quantities measured directly.
- **Inferred**: judgements about how the video was made or where material came from, with a probability and the basis for it. The basis may be measurements a person cannot see (frame rate, noise, transcoding, metadata).

In the timeline, a key ending in `~` is inferred and a key without it is seen or measured. In shot files, inferred fields live under `inferred`, and the body SHOULD give seen and inferred their own sections. When the two disagree, the frames win.

## 7. The timeline (L2)

`video/timeline.md` MUST contain a fenced code block with the info string `videomd-timeline`. Each non-empty line in it is one shot:

```
#07 16.2-18.5 | seen man talking, chat screenshots pop up | camera static | made~ screen capture 41% · runner-up code render 29% | flag low confidence
```

```
line   = head *( " | " field )
head   = "#" number " " seconds "-" seconds
field  = key [ "~" ] " " value
key    = a lowercase letter, then lowercase letters, digits, "_" or "-"
value  = one or more characters, none of them "|"
```

- Shot numbers MUST be strictly increasing. The end time MUST NOT be earlier than the start time. Times are seconds from the start of the video.
- A value MUST NOT contain `|`; producers replace it, for example with `/`.
- Keys SHOULD appear in the order of the table below. A key with nothing to say is left out. Only the head is required.

| Key | Meaning | Kind |
|---|---|---|
| `story` | The shot's job in the story and the point it makes | seen |
| `seen` | What is on screen, one sentence | seen |
| `camera` | Camera movement | measured |
| `overlay` | Overlays: subtitles, titles, stickers… | measured |
| `made~` | How the shot was made, with a probability; a runner-up MAY follow ` · ` | inferred |
| `material~` | Where the material came from: generated, the creator's own footage, stock… | inferred |
| `remake` | How to remake the shot | plan |
| `flag` | Why the shot needs a second look | — |
| `x-<name>` | Producer-defined | any |

Timeline values are prose for models, in the package's `lang`. Programs that need stable values read the shot files.

## 8. Shot files (L3)

`video/shots/<n>.md` describes one shot. Its front matter is the shot's data; only `shot`, `time` and `tokens` are required:

```yaml
---
videomd: 1
part: shot
shot: 7
time: [16.2, 18.467]
camera: static
overlays: [subtitle]
inferred:
  made: screen_capture
  p: 0.408
  alternatives: {code_render: 0.294, live_action: 0.209}
  decided_by: model
  real_material: true
flags: [low_confidence]
frames: {sheet: shots/shot_007.jpg, first: shots/shot_007_first.jpg, last: shots/shot_007_last.jpg}
tokens: 572
---
```

| Field | Required | Meaning |
|---|---|---|
| `shot` | yes | Shot number; equals the number in the file name |
| `time` | yes | `[start, end]` in seconds |
| `camera` | no | Camera id ([TAXONOMY.md](TAXONOMY.md)) |
| `overlays` | no | Overlay ids ([TAXONOMY.md](TAXONOMY.md)) |
| `inferred` | no | The production-method verdict. When present, `made` (a method id) and `p` (its probability) are required |
| `inferred.alternatives` | no | Other method ids to their probabilities |
| `inferred.decided_by` | no | Who made the final call: `tools`, `model`, `agent` or `human` |
| `inferred.real_material` | no | Whether the shot contains real material the creator had to obtain: footage, photos, screenshots |
| `flags` | no | `uncertain`, `disputed`, `low_confidence` |
| `frames` | no | Paths to images of the shot: `sheet` (a contact sheet), `first`, `last`, or other names |

The body is Markdown for models. It SHOULD contain, in this order: what is seen, what is inferred and why, and how to remake the shot.

## 9. Extensions

- Production-method, camera, reader and flag ids outside [TAXONOMY.md](TAXONOMY.md) MUST start with `x-`, e.g. `x-game_capture`. A reader treats an id it does not know as unknown. Overlay ids are open and need no prefix.
- Producer-defined topic files are named `video/x-<name>.md` with `part: x-<name>`; producer-defined timeline keys are `x-<name>`.
- A reader MUST ignore fields, keys, files and ids it does not know, and MUST NOT fail because of them.
- An `x-` id used by more than one producer is a candidate for the taxonomy (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## 10. Conformance

A directory is a conforming VIDEO.md package if and only if:

1. `VIDEO.md` exists and its front matter matches `card` in the schema.
2. `VIDEO.md` has a `videomd-map` block; every line follows the grammar in section 5; every path in it is relative to the package; every non-pattern path exists; every pattern matches at least one file; every `.md` file directly under `video/` is covered.
3. Every `.md` file directly under `video/` has front matter that matches `part`.
4. `video/timeline.md` has a `videomd-timeline` block; every line follows the grammar in section 7; shot numbers are strictly increasing; no shot ends before it starts; the number of lines equals `shots` in the card.
5. Every timeline line has a shot file with the same number whose front matter matches `shot`, and whose times agree with the line within 0.06 seconds.
6. Every shot file under `video/shots/` has a timeline line, and the number in its name equals its `shot`.
7. Every path under `frames` in a shot file is relative to the package and exists.

A producer MUST write conforming packages. To check one:

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](https://github.com/videomd/videomd/tree/main/conformance/) has packages that conform and packages that each break one rule; an implementation of a validator SHOULD give the same results.

## 11. Versioning

`videomd: 1` is this version. Adding optional fields, keys, topic files or taxonomy ids does not change it; readers ignore what they do not know. Changing the meaning of a field, the grammar of the map or the timeline, or the layout increases it.
