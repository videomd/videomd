# VIDEO.md specification, version 1

This document defines the VIDEO.md package: a directory that describes one video for models and programs. Its goals are in [DESIGN.md](DESIGN.md).

The key words MUST, MUST NOT, SHOULD and MAY are used as in RFC 2119.

## 1. Overview

A package is a directory with an entry file `VIDEO.md` and a folder `video/`. It is read in levels, each more detailed and more expensive than the one before:

| Level | Where | Typical size | Answers |
|---|---|---|---|
| L0 card | `VIDEO.md` front matter | ~150 tokens | What the video is, how it was made, how sure |
| L1 overview and map | `VIDEO.md` body | 1–2k tokens | The verdict, the open questions, and which file to open next |
| L2 topics | `video/<topic>.md` | hundreds to thousands | One aspect in full; `video/timeline.md` has one line per shot |
| L3 shots | `video/shots/<n>.md` | 500–1000 each | One shot: what is seen, what is inferred and why, frames |
| L4 raw | anything else in the directory | any | Data and media for programs; defined by the producer |

A reader SHOULD start at L0 and open the next level only when the question needs it.

## 2. Layout

```
<package>/
  VIDEO.md             L0 card (front matter) + L1 overview and map (body)
  video/
    timeline.md        L2, required: one line per shot
    content.md         L2, optional: what the video says, structure, script
    cast.md            L2, optional: characters, scenes, props
    sound.md           L2, optional: voice, music, sound effects, beats
    look.md            L2, optional: framing, camera, lighting, editing of filmed shots
    packaging.md       L2, optional: subtitles, styled text, stickers, picture-in-picture
    remake.md          L2, optional: how to remake the video
    x-<name>.md        L2, optional: producer-defined topics
    shots/01.md        L3, required: one file per shot
  ...                  L4, optional: producer-defined (raw data, frames, audio stems, subtitle files)
```

- All paths in a package, including paths written inside `video/`, MUST be relative to the package root, MUST NOT start with `/` and MUST NOT contain `../`.
- A producer SHOULD NOT write a topic file that has nothing in it.
- Shot files are named by shot number, zero-padded to at least two digits: `01.md`, `02.md`, … `120.md`.

## 3. Front matter

Every `.md` file in a package MUST start with YAML front matter between two `---` lines. Every front matter MUST contain the format version:

```yaml
videomd: 1
```

Files under `video/` MUST also contain:

```yaml
part: timeline   # which part this is: timeline, content, cast, sound, look, packaging, remake, shot, or x-<name>
tokens: 2275     # approximate size of the body in tokens
```

`tokens` is an estimate so a reader can decide before opening the file. Producers MAY use any tokenizer. One that needs none: ASCII characters ÷ 4 + other characters × 0.75.

The exact fields of each front matter are given in [schema/videomd-1.schema.json](schema/videomd-1.schema.json) (JSON Schema 2020-12): `card` for `VIDEO.md`, `part` for topic files, `shot` for shot files.

## 4. The card (L0)

The front matter of `VIDEO.md`:

```yaml
videomd: 1
name: coffee-ad
description: Mixed — filmed 70% + code-rendered text card 30%
source: {file: coffee-ad.mp4, duration: 10.0, size: 1080x1920, fps: 30.0, aspect: '9:16'}
shots: 2
confidence: 0.84                              # duration-weighted confidence of the verdicts
made_mix: {live_action: 0.7, code_render: 0.3}   # inferred, share of duration
readers: [tools, model]                       # who took part in the verdicts
open_questions: 1
lang: en
generator: {name: rea-video, version: 0.1.0}
```

| Field | Required | Meaning |
|---|---|---|
| `videomd` | yes | Format version, `1` |
| `name` | yes | Short name of the video |
| `description` | yes | One line, at most 200 characters: what it is and how it was made |
| `source` | yes | `file` and `duration` (seconds) required; `url`, `size` (`WxH`), `fps`, `aspect` optional |
| `shots` | yes | Number of shots; equals the number of timeline lines |
| `made_mix` | yes | Production methods ([TAXONOMY.md](TAXONOMY.md)) to their share of the duration |
| `lang` | yes | Language of the text written for models, e.g. `en`, `zh` |
| `confidence` | no | 0–1 |
| `readers` | no | Any of `tools` (measurements), `model` (an image or video model), `agent` (an agent that looked at the frames), `human` |
| `open_questions` | no | Number of points that need a second look |
| `generator` | no | `name` and `version` of the producer |

## 5. The overview and the map (L1)

The body of `VIDEO.md` is free Markdown for models. It SHOULD contain, in this order: the verdict, the open questions, the map, and a short note on how to read the package.

The map is a Markdown table. Each row starts with a path in backticks:

```
| File | What is in it | When to read it | ~tokens |
|---|---|---|---|
| `video/timeline.md` | One line per shot | Which shot does what | 2049 |
| `video/shots/01.md … 21.md` | Per-shot detail | Checking one shot | 570 |
| `shots/, stems/` | Frames, audio stems | Checking by eye | — |
```

A row whose path contains `…` stands for a range of files; a row whose path contains `,` lists several. Every other path in the map MUST exist.

## 6. Seen and inferred

A package keeps two kinds of statements apart:

- **Seen**: what is visible or audible and can be checked against the frames (what is on screen, camera movement, overlays, text), and quantities measured directly.
- **Inferred**: judgements about how the video was made or where material came from, with a probability and the basis for it. The basis may be measurements a person cannot see (frame rate, noise, transcoding, metadata).

In the timeline, a key ending in `~` is inferred; a key without it is seen or measured. In shot files, inferred fields live under `inferred`, and the body SHOULD give seen and inferred their own sections. When the two disagree, the frames win.

## 7. The timeline (L2)

`video/timeline.md` MUST contain exactly one fenced code block with the info string `videomd-timeline`. Each non-empty line in it is one shot:

```
#07 16.2-18.5 | seen man talking, chat screenshots pop up | cam static | made~ screen capture(screen_capture) 41% · runner-up code render 29% | flag low confidence
```

Grammar:

```
line   = head *( " | " field )
head   = "#" number " " seconds "-" seconds
field  = key [ "~" ] " " value
key    = lowercase letter *( lowercase letter / digit / "_" / "-" )
value  = one or more characters, none of them "|"
```

- Shot numbers MUST be strictly increasing. The end time MUST NOT be earlier than the start time.
- A value MUST NOT contain `|`. Producers replace it, for example with `/`.
- Keys SHOULD appear in the order of the table below; a missing key is left out.

| Key | Meaning | Kind |
|---|---|---|
| `say` | The shot's job in the story and the point it makes | seen |
| `seen` | What is on screen, one sentence | seen |
| `cam` | Camera movement | measured |
| `over` | Overlays: subtitles, titles, stickers… | measured |
| `made~` | Production method and its probability. The method id from [TAXONOMY.md](TAXONOMY.md) MUST be in parentheses. A runner-up MAY follow ` · ` | inferred |
| `real~` | Where the material came from: generated, the creator's own footage, mixed… | inferred |
| `remake` | Remake route | plan |
| `flag` | Why the shot needs a second look | — |

Values are written for models, in the package's `lang`. Programs that need stable values read the shot files or the id in parentheses after `made~`.

Readers MUST ignore keys they do not know. New keys MAY be added in later minor revisions.

## 8. Shot files (L3)

`video/shots/<n>.md` holds one shot. Its front matter is the shot's data:

```yaml
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
```

| Field | Required | Meaning |
|---|---|---|
| `shot`, `time` | yes | Shot number and `[start, end]` in seconds |
| `inferred.made`, `inferred.p` | yes | Production method id and its probability |
| `inferred.alternatives` | no | Other method ids to probabilities |
| `inferred.decided_by` | no | Who made the final call: `tools`, `model`, `agent` or `human` |
| `inferred.real_material` | no | Whether the shot contains real material (footage, photos, screenshots) the creator had to obtain |
| `camera` | no | Camera id ([TAXONOMY.md](TAXONOMY.md)) |
| `overlays` | no | Overlay ids ([TAXONOMY.md](TAXONOMY.md)) |
| `flags` | no | `uncertain`, `disputed`, `low_confidence` |
| `frames` | no | `sheet`, `first`, `last`: paths to images of the shot |

The body is free Markdown. It SHOULD contain, in this order: what is seen, what is inferred and why, and how to remake the shot.

## 9. Extensions

- Method, camera, reader and flag ids outside [TAXONOMY.md](TAXONOMY.md) MUST start with `x-`, e.g. `x-game_capture`. Readers treat an id they do not know as unknown.
- Producer-defined topic files are named `video/x-<name>.md` and use `part: x-<name>`.
- Any front matter MAY carry fields that are not in the schema. Readers MUST ignore fields, keys and files they do not know.
- An `x-` id that several producers use is a candidate for the next revision of the taxonomy.

## 10. Conformance

A directory is a conforming VIDEO.md package if and only if:

1. `VIDEO.md` exists and its front matter matches `card` in the schema.
2. Every path in the map of `VIDEO.md` exists (rows with `…` or `,` excepted).
3. Every `.md` file directly under `video/` has front matter that matches `part`.
4. `video/timeline.md` has a `videomd-timeline` block; every line in it follows the grammar in section 7; shot numbers are strictly increasing; no shot ends before it starts; the number of lines equals `shots` in the card.
5. For every timeline line there is a shot file with the same number whose front matter matches `shot`; its number and times agree with the line (within 0.06 s); the id in parentheses after `made~` equals `inferred.made`.
6. Every path under `frames` in a shot file exists.

A producer MUST write packages that conform. A reader MUST NOT fail on content it does not know.

Checking a package:

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](conformance/) has packages that conform and packages that each break one rule.

## 11. Versioning

`videomd: 1` is this version. Adding fields, keys, topic files or taxonomy ids does not change the number; readers ignore what they do not know. Changing the meaning of an existing field, the timeline grammar or the layout increases it.
