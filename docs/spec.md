# VIDEO.md specification

This document defines the VIDEO.md package: a directory that describes one video for models and programs. For what it is and why, read the [README](https://github.com/videomd/videomd/blob/main/README.md) and [design notes](design.md). For how to write one, [authoring guide](authoring.md); for how to use one in an agent or app, [integration guide](integrate.md).

The key words MUST, MUST NOT, SHOULD and MAY are used as in RFC 2119.

## 1. Levels

A package is read in levels, each more detailed and more expensive than the one before:

| Level | Where | Typical size | Answers |
|---|---|---|---|
| L0 card | `VIDEO.md` front matter | 100–300 tokens | What the video is about and whether to open it |
| L1 overview and map | `VIDEO.md` body | 1–2k tokens | The verdict, the open questions, which file to open next |
| L2 scenes | `video/scenes.md` | one line per scene | For long videos: the parts of the video, read before the timeline |
| L2 topics | `video/<topic>.md` | hundreds to thousands | One aspect in full; `video/timeline.md` has one line per shot |
| L3 shots | `video/shots/<n>.md` | hundreds each | One shot in full |
| L4 raw | anything else in the directory | any | Data and media for programs, defined by the producer |

A reader SHOULD start at L0 and open the next level only when the question needs it.

## 2. Layout

```
<package>/
  VIDEO.md             required   L0 card + L1 overview and map
  video/
    scenes.md          optional   L2 one line per scene, for long videos
    timeline.md        required   L2 one line per shot, or a note that the timeline is split
    timeline/01.md     optional   L2 one part of a split timeline
    content.md         optional   L2 what the video says, structure, script
    cast.md            optional   L2 characters, scenes, props
    sound.md           optional   L2 voice, music, sound effects, beats
    look.md            optional   L2 framing, camera, lighting, editing of filmed shots
    packaging.md       optional   L2 subtitles, styled text, stickers, picture-in-picture
    remake.md          optional   L2 how to remake the video
    x-<name>.md        optional   L2 producer-defined topics
    shots/01.md        required   L3 one file per shot
    transcript.vtt     optional   L4 who says what, when (WebVTT), when named in the card
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

`part` is `timeline`, `scenes`, `content`, `cast`, `sound`, `look`, `packaging`, `remake`, `shot`, or `x-<name>`. `tokens` is an estimate so a reader can decide before opening the file; producers MAY use any tokenizer. One that needs none: ASCII characters ÷ 4 + other characters × 0.75.

The fields of each kind of front matter are defined by [schema/videomd-1.schema.json](https://github.com/videomd/videomd/blob/main/schema/videomd-1.schema.json) (JSON Schema 2020-12): `card` for `VIDEO.md`, `part` for topic files, `shot` for shot files. Front matter MAY carry fields the schema does not define.

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

Cards of long or related videos may also carry `scenes`, `tracks`, `related` and `source.projection`:

```yaml
scenes: 2
tracks: {transcript: video/transcript.vtt}
related:
  - {rel: part_of, name: harbour-stories}
  - {rel: remake_of, url: https://example.com/films/harbour-1962}
source: {file: harbour-night.mp4, duration: 300.0, projection: flat}
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
| `made_mix` | no | Production-method ids ([taxonomy](taxonomy.md)) to their share of the duration |
| `confidence` | no | 0–1, how sure the verdicts are overall |
| `readers` | no | Who took part in the verdicts: `tools`, `model`, `agent`, `human` |
| `open_questions` | no | Number of points that need a second look |
| `generator` | no | `name` and `version` of the producer |
| `source.projection` | no | `flat` (the default), `equirectangular`, `cubemap` or `fisheye`, for 360° and VR video |
| `scenes` | no | Number of scenes; equals the lines in `video/scenes.md` (section 9) |
| `tracks` | no | Paths to standard tracks. `transcript`: a WebVTT file (section 13) |
| `related` | no | Other videos this one relates to (section 13) |

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

The timeline lists every shot, one per line, in a fenced code block with the info string `videomd-timeline`:

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
| `layers` | For a composite picture: what each layer shows and where (section 11) | seen |
| `camera` | Camera movement, including several moves in order: `orbit, then whip pan right` (section 12) | measured |
| `transition` | How the shot is joined to the one before, when it is not a plain cut (section 12) | measured |
| `overlay` | Overlays: subtitles, titles, stickers… | measured |
| `made~` | How the shot was made, with a probability; a runner-up MAY follow ` · ` | inferred |
| `material~` | Where the material came from: generated, the creator's own footage, stock… | inferred |
| `remake` | How to remake the shot | plan |
| `flag` | Why the shot needs a second look | — |
| `x-<name>` | Producer-defined | any |

Timeline values are prose for models, in the package's `lang`. Programs that need stable values read the shot files.

**Where the timeline lives.** For most videos, the block is in `video/timeline.md`. A long video MAY split it into parts, `video/timeline/01.md`, `02.md` …, usually one per scene. Then each part has `part: timeline`, its own `shots` count and a `videomd-timeline` block, `video/timeline.md` holds no block (only its front matter, with `shots` for the whole video, and a note on how the timeline is split), and the parts read in file-name order form the timeline. A package MUST NOT have both a block in `video/timeline.md` and parts.

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
| `camera` | no | A camera id, or a camera object with `rig` and `moves` (section 12) |
| `overlays` | no | Overlay ids ([taxonomy](taxonomy.md)) |
| `inferred` | no | The production-method verdict. When present, `made` (a method id) and `p` (its probability) are required |
| `inferred.alternatives` | no | Other method ids to their probabilities |
| `inferred.decided_by` | no | Who made the final call: `tools`, `model`, `agent` or `human` |
| `inferred.real_material` | no | Whether the shot contains real material the creator had to obtain: footage, photos, screenshots |
| `flags` | no | `uncertain`, `disputed`, `low_confidence` |
| `frames` | no | Paths to images of the shot: `sheet` (a contact sheet), `first`, `last`, or other names |
| `scene` | no | The scene the shot belongs to (section 9) |
| `take`, `beats` | no | One continuous take split into shots; moments inside the shot (section 10) |
| `layers` | no | The parts of a composite picture (section 11) |
| `transition_in`, `speed`, `lens` | no | How the shot is joined to the one before; slow motion, ramps, reverse; lens and focus effects (section 12) |

The body is Markdown for models. It SHOULD contain, in this order: what is seen, what is inferred and why, and how to remake the shot.

## 9. Scenes and long videos

A film or a long stream has hundreds or thousands of shots; its timeline is too long to read in one go. Such a package SHOULD have `video/scenes.md`, the parts of the video in a fenced block with the info string `videomd-scenes`, one per line:

```
#S01 0.0-120.0 | shots 1-4 | story waiting on the harbour | seen night, lanterns, a moored boat
#S02 120.0-300.0 | shots 5-6 | story the storm and the walk home
```

```
line   = "#S" number " " seconds "-" seconds " | shots " first "-" last *( " | " field )
```

- `part: scenes` and `scenes` (the number of lines) are required in its front matter; if the card has `scenes`, it is the same number.
- Scenes MUST be in order and cover every shot of the timeline exactly once, without gaps or overlaps. A scene starts when its first shot starts and ends when its last shot ends.
- A shot file MAY give its `scene`; it MUST then agree with `video/scenes.md`.
- Fields after `shots` use the timeline's keys. A "scene" here is any part a reader would look for: a scene of a film, a chapter of a lecture, a segment of a stream.

A reader of a long video reads `video/scenes.md` first, then only the timeline lines, or the timeline part, of the scene the question is about.

## 10. Long takes

A timeline line is usually a shot between two cuts. A long take (a vlog walk, a stream, a one-take music video, an hour of screen recording) MAY be split by content into several timeline lines, so that each line still says one thing. Each of these shot files carries the same `take` number; shots of one take MUST follow one another, each starting where the one before ends.

Inside any shot, `beats` mark moments worth finding without splitting the shot further:

```yaml
take: 1
beats:
  - {time: [120.0, 150.0], what: rain starts on the pier}
  - {time: [150.0, 210.0], what: he walks along the sea wall}
```

Every beat MUST lie inside its shot.

## 11. Layers

A composite picture shows several sources at once: split screen, picture-in-picture, a webcam over gameplay, a reaction over a trailer, a presenter keyed over a slide. `layers` describes each part:

```yaml
layers:
  - {id: trailer, role: base, region: [0, 0, 1, 1], seen: game trailer, made: screen_capture, p: 0.9, real_material: true}
  - {id: webcam, role: pip, region: [0.72, 0.68, 0.26, 0.3], seen: host on a webcam, made: live_action, p: 0.95}
```

| Field | Meaning |
|---|---|
| `id` | Required. Unique within the shot; the same id in several shots is the same source |
| `role` | `base`, `pip`, `split`, `inset`, `background`, `foreground`, `overlay`, or an `x-` id |
| `region` | `[x, y, w, h]` as fractions of the frame, origin top left; MUST lie inside the frame |
| `seen` | What the layer shows |
| `made`, `p`, `real_material` | The layer's production method, its probability, and whether it is real material (inferred) |
| `camera` | The layer's own camera, as in section 12 |

When `layers` is present, `inferred.made` still describes the shot as a whole: the method of the layer that covers most of the frame.

## 12. Camera, transitions, speed and lens

**Camera.** `camera` is either a camera id ([taxonomy](taxonomy.md)) or an object that names the rig and lists the moves in order:

```yaml
camera:
  rig: virtual
  moves:
    - {type: orbit, direction: cw, speed: medium, time: [12.0, 19.6]}
    - {type: whip_pan, direction: right, speed: fast, time: [19.6, 20.0]}
```

- `rig` is what carries the camera: `tripod`, `handheld`, `gimbal`, `dolly`, `crane`, `drone`, `fpv`, `vehicle`, `screen`, `virtual` (3D, games, generated video), `unknown`.
- Each move has a `type` ([taxonomy](taxonomy.md)) and MAY have `direction` (`left`, `right`, `up`, `down`, `in`, `out`, `cw`, `ccw`), `speed` (`slow`, `medium`, `fast`) and `time`, which MUST lie inside the shot.
- Camera describes the motion as it appears in the picture, whether a real camera or a virtual one made it.

**Transitions.** `transition_in` says how the shot is joined to the one before when it is not a plain cut. Its `type` is from the taxonomy (`dissolve`, `wipe`, `whip`, `match_cut`, `morph`, `mask` …); its `time`, when given, MUST span the start of the shot. A whip-pan transition usually starts in the last frames of the shot before.

```yaml
transition_in: {type: whip, time: [19.6, 20.3]}
```

**Speed.** `speed` gives the playback: `rate` (1 is real time, 0.25 is quarter speed, 8 is a time-lapse), `ramp` (the speed changes within the shot), `reverse`, `freeze`.

**Lens.** `lens` lists lens and focus effects seen in the shot: `rack_focus`, `shallow_focus`, `deep_focus`, `fisheye`, `wide`, `telephoto`, `tilt_shift`, `anamorphic`, `macro`. The list is open.

## 13. Tracks and related videos

**Transcript.** When the card names `tracks.transcript`, that file MUST exist and be WebVTT. Speakers SHOULD be marked with voice tags, `<v Name>`. A transcript lets a program find who says what without reading prose, and lets a model quote speech with times.

```
WEBVTT

00:00:41.000 --> 00:00:44.000
<v Fisherman>Not tonight, then.
```

**Related videos.** `related` lists other videos, each with a `rel` and at least one of `sha256`, `url` or `name`:

| `rel` | This video is… |
|---|---|
| `same_video` | the same video, for example a re-upload |
| `remake_of` | a remake of the other |
| `part_of` | an episode or part of the other (a series, a playlist) |
| `clip_of` | cut from the other |
| `source_of` | the source the other was cut or remade from |
| `sequel_of` | a follow-up to the other |
| `translation_of` | the other in another language |

## 14. Extensions

- Production-method, camera, rig, move, transition, layer-role, relation, reader and flag ids outside [taxonomy](taxonomy.md) MUST start with `x-`, e.g. `x-game_capture`. A reader treats an id it does not know as unknown. Overlay and lens ids are open and need no prefix.
- Producer-defined topic files are named `video/x-<name>.md` with `part: x-<name>`; producer-defined timeline keys are `x-<name>`; producer-defined tracks use their own names under `tracks`.
- A reader MUST ignore fields, keys, files and ids it does not know, and MUST NOT fail because of them.
- An `x-` id used by more than one producer is a candidate for the taxonomy (see [CONTRIBUTING.md](https://github.com/videomd/videomd/blob/main/CONTRIBUTING.md)).

## 15. Conformance

A directory is a conforming VIDEO.md package if and only if:

1. `VIDEO.md` exists and its front matter matches `card` in the schema.
2. `VIDEO.md` has a `videomd-map` block; every line follows the grammar in section 5; every path in it is relative to the package; every non-pattern path exists; every pattern matches at least one file; every `.md` file directly under `video/`, and every timeline part, is covered.
3. Every `.md` file directly under `video/`, and every timeline part, has front matter that matches `part`.
4. The timeline is either a `videomd-timeline` block in `video/timeline.md` or parts under `video/timeline/`, not both; every line follows the grammar in section 7; shot numbers are strictly increasing; no shot ends before it starts; the number of lines equals `shots` in the card.
5. Every timeline line has a shot file with the same number whose front matter matches `shot`, and whose times agree with the line within 0.06 seconds.
6. Every shot file under `video/shots/` has a timeline line, and the number in its name equals its `shot`.
7. Every path under `frames` in a shot file is relative to the package and exists.
8. Beats and camera moves lie inside their shot; `transition_in.time` spans the start of its shot; layer regions lie inside the frame and layer ids are unique within a shot.
9. Shots with the same `take` follow one another without gaps.
10. If `video/scenes.md` exists, it has a `videomd-scenes` block whose lines follow the grammar in section 9, are in order, cover every shot exactly once and agree with the shots' times and `scene` fields; its count agrees with the card. If the card has `scenes`, `video/scenes.md` exists.
11. Every path under `tracks` exists; `tracks.transcript` is a WebVTT file.

A producer MUST write conforming packages. To check one:

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](https://github.com/videomd/videomd/tree/main/conformance/) has packages that conform and packages that each break one rule; an implementation of a validator SHOULD give the same results.

## 16. Versioning

`videomd: 1` is this version. Adding optional fields, keys, topic files or taxonomy ids does not change it; readers ignore what they do not know. Changing the meaning of a field, the grammar of the map or the timeline, or the layout increases it.
