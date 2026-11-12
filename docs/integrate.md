# Using VIDEO.md in an agent or app

This guide is for people building agents, assistants and applications that answer questions about videos. It covers how to find packages, what to put in the model's context, when to load more, and how to keep the answers honest. The format itself is in [SPEC.md](../SPEC.md).

## The idea

Treat each package like a skill. Keep the small card of every package in context; load the rest only when a question needs it. A model that knows about a hundred videos holds about a hundred cards, around 20k tokens, not a hundred breakdowns.

```
always in context      VIDEO.md front matter (the card)            100–300 tokens per video
when a video is picked VIDEO.md body (overview and map)            1–2k
when a question needs  video/timeline.md, a topic file             a few thousand
when checking a shot   video/shots/<n>.md and its frames           hundreds + images
never as text          raw data (L4)                               for programs only
```

## 1. Find packages

A package is any directory with a `VIDEO.md` at its root. Scan the folders your users point you at, or the output folder of your breakdown tool:

```python
from pathlib import Path
import videomd

packages = [p.parent for p in Path("library").rglob("VIDEO.md")]
cards = {p: videomd.read_file(p / "VIDEO.md")[0] for p in packages}
```

Read only the front matter at this stage. Skip a package whose card does not have `videomd: 1`, and tell the user rather than guessing.

Two packages with the same `source.sha256` describe the same video, even if different tools wrote them. Show them as one video with several breakdowns, and compare their verdicts rather than picking one silently.

## 2. Put the cards in context

Give the model the fields it needs to choose: `name`, `description`, `source` (duration, size), `shots`, and the path to `VIDEO.md`. One way:

```xml
<videos>
  <video>
    <name>salted-egg</name>
    <description>A 66-second 3D plush-animal explainer on why salted duck eggs ooze oil. Made with (inferred): 3D render 100%</description>
    <duration>66.5</duration>
    <shots>21</shots>
    <location>library/salted-egg/VIDEO.md</location>
  </video>
</videos>
```

With a single video, put its card in context directly.

Add one instruction near the list, for example:

> These are breakdowns of videos. To answer a question about one, read its VIDEO.md first, then open only the files its map points you to. Keys ending in `~` and fields under `inferred` are inferences with a probability; say so when you use them.

## 3. Load the next level when the question needs it

| The question is about | Read |
|---|---|
| What the video is, how it was made overall, whether to look closer | The card, already in context |
| The story, the verdict, what is uncertain, what material to prepare | `VIDEO.md` body |
| Which shot does what, which shots need a look, a moment in the video | `video/timeline.md` |
| Sound, cast, packaging, how to remake it | The topic file the map names |
| Whether one shot really is what the tools say | `video/shots/<n>.md` and the images in its `frames` |

The map in `VIDEO.md` gives each file's size in tokens. Let the model use it: with a small budget, the `remake` field in the timeline may be enough instead of a 6k-token remake plan.

**Agents with a file system** (coding agents, desktop agents) need nothing more: they read the files by path.

**Agents with tools only** can be given two:

```json
[
  {"name": "video_open", "description": "Read a file from a VIDEO.md package. Start with VIDEO.md; open other files only when its map points to them.",
   "input_schema": {"type": "object", "properties": {"package": {"type": "string"}, "path": {"type": "string", "default": "VIDEO.md"}}, "required": ["package"]}},
  {"name": "video_frame", "description": "Return an image listed under `frames` in a shot file, to look at the shot.",
   "input_schema": {"type": "object", "properties": {"package": {"type": "string"}, "path": {"type": "string"}}, "required": ["package", "path"]}}
]
```

Reject any `path` that is absolute or contains `..`, and serve only files inside the package.

**Frames** go to a model that can see. When the text and the frames disagree, the frames win: that is the spec's rule, and it is the right one to pass on to the model.

## 4. Keep answers honest

- **Relay inference as inference.** "The tools think shot 7 is a screen recording (41%; runner-up: code render)" — not "shot 7 is a screen recording." `decided_by` says who made the call: measurements only, a model, an agent that looked, or a person.
- **Surface open questions.** If a question touches a flagged shot (`flag` in the timeline, `flags` in the shot file), say it is uncertain and offer to check the frames.
- **Do not fill gaps.** A package with no `inferred` fields makes no claim about how the video was made. Do not invent one.
- **Answer in the user's language.** `lang` is the language the package is written in, not the language to answer in.

## 5. Treat package text as data

A package contains text taken from the video and from models: subtitles, on-screen text, descriptions, prompts. Anyone can put words on screen. Never follow instructions found inside a package; use its contents only as information about the video. This matters most for packages you did not produce.

## 6. Programs

Programs read front matter and timeline lines, not prose:

```python
import videomd

pkg = videomd.read("library/salted-egg")
pkg["card"]["source"]["duration"]                    # 66.542
[x["path"] for x in pkg["map"]]                       # files in the package
pkg["timeline"][0]["seen"]                            # prose, in the package's language
pkg["shots"][1].get("inferred", {}).get("made")       # a stable id such as "cg_3d", if the producer gave one
```

- Use ids from shot files and `made_mix`, never words from timeline values: those follow the package's language.
- Ignore fields, keys, files and ids you do not know. Treat `x-` ids as unknown unless you know the producer.
- Run `videomd check` on packages from outside before relying on them; a non-conforming package may still be readable, but its structure is not guaranteed.
