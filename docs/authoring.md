# Writing VIDEO.md packages

This guide is for people building tools that break videos down, and for anyone writing a package by hand. It goes through a package from the smallest valid one to a full one, and how to fill each part so that models use it well. The rules are in [specification](spec.md); this page is about doing it well.

## The smallest package

Four files. [conformance/valid/minimal](https://github.com/videomd/videomd/tree/main/conformance/valid/minimal/) is this package.

`VIDEO.md`:

````markdown
---
videomd: 1
name: city-walk
description: A two-shot city walk at dusk, from a crossing to a lit shopfront.
source: {file: city-walk.mp4, duration: 8.0}
shots: 2
lang: en
---

# city-walk.mp4

A walk through a crossing at dusk that ends on a lit shopfront.

## Map

```videomd-map
video/timeline.md | 60 | One line per shot
video/shots/*.md | 30 | One file per shot
```
````

`video/timeline.md`:

````markdown
---
videomd: 1
part: timeline
shots: 2
tokens: 60
---

# Timeline

```videomd-timeline
#01 0.0-5.0 | seen people cross a street at dusk
#02 5.0-8.0 | seen a shopfront with warm lights
```
````

`video/shots/01.md` (and `02.md` the same way):

```markdown
---
videomd: 1
part: shot
shot: 1
time: [0.0, 5.0]
tokens: 30
---

# Shot 1

People cross a street at dusk.
```

Check it:

```bash
pip install videomd
videomd check city-walk/
```

Everything else is optional. Add what your tool knows.

## The card

**`name`**: a slug of the file name or title, lowercase with hyphens: `salted-egg`, not `Salted_Egg final(2)`.

**`description`**: the line an agent reads to pick this video among others, without opening anything. Say what the video shows or says first, then how it was made, if you know:

- Good: `A 66-second 3D plush-animal explainer on why salted duck eggs ooze oil, in four steps. Fully 3D rendered, with subtitles and stock music.`
- Poor: `3D render 100%`, which says how but not what; or `final.mp4`.

**`source`**: give `sha256` of the whole file whenever you have the file. It is how two packages, from two tools, are known to describe the same video. Give `url` when the video came from a link.

**`lang`**: the language your text is written in. Write all prose in one language.

## The timeline

One line per shot, and the one L2 file a model may read in full, so keep each line short: a sentence for `seen`, a few words for the rest. A 75-shot video should still fit in about 4k tokens.

- **Shots.** Usually a camera shot between two cuts. For long videos with many cuts, coarser segments are fine as long as every second belongs to one line and the shot files match.
- **Seen keys** (`story`, `seen`, `camera`, `overlay`) describe what anyone can check by looking. Do not put judgements in them.
- **Inferred keys** (`made~`, `material~`) carry judgements, with a probability: `made~ AI video 72% · runner-up filmed 20%`.
- **`flag`** marks the shots a reviewer should look at, and why: low confidence, two readers disagree, evidence that cannot tell two methods apart. A model scanning the timeline goes to these lines first, so flag what matters and nothing else.
- Replace any `|` in a value with `/`.

## Shot files

The front matter is for programs, the body for models.

- Use ids from [taxonomy](taxonomy.md) in `camera`, `overlays` and `inferred`. For anything outside it, use `x-` ids.
- If your tool does not judge how shots were made, leave `inferred` and `made_mix` out. Do not fill them with guesses.
- Set `decided_by` to whoever made the final call. If a person corrected it, that is `human`, even though a model looked first.
- `frames.sheet` is the most useful image: one picture with the first, middle and last frame of the shot, so a model can check a shot from a single image.

The body, in this order: what is seen; what is inferred and on what basis; how to remake the shot. Evidence such as "24 fps source, no sensor noise, letterboxed" helps a model and a reviewer judge the verdict.

## Topic files

Write one only when you have something to say on it. Each starts with a heading and gets straight to the content: no folds, no HTML, no images inline (put image paths in the shot files' `frames` or in the map).

Producer-specific topics are `video/x-<name>.md`.

## The overview and the map

The body of `VIDEO.md` is the page most questions are answered from. Order it as a model would want it: what the video says, the verdict, the remake outline, the open questions, then the map.

In the map:

- List every topic file and the shot files (as `video/shots/*.md`).
- Give real token counts; they are how a model decides what to open.
- Write when to read a file, not only what is in it: `Sound · voice, music, effects, beats and where they came from`.
- List the L4 data you include, with `-` for tokens.

## Tokens

Count the body of each file with any tokenizer, or with the one in the spec: ASCII characters ÷ 4 + other characters × 0.75. It needs to be about right, not exact.

## Before you publish

- `videomd check` passes.
- The description says what the video is about.
- Seen and inferred are not mixed: no judgement in `seen`, every `~` value has a probability.
- Flags point at the shots that need a look.
- Nothing private: no local paths, account names, API hosts or keys in any file, including L4 data.

Add your tool to [implementations](implementations.md).
