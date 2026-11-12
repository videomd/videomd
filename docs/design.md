# Why VIDEO.md looks the way it does

[SPEC.md](../SPEC.md) says what a package contains. This page says why: the problem it solves, where the ideas come from, and the reasoning behind each decision.

## In one line

Every skill has a `SKILL.md`; every video gets a `VIDEO.md`. It starts with a card of a few hundred tokens and opens up, level by level, down to a single shot. Every level says how big it is, and keeps what was seen apart from what was inferred.

The card is the video's ID card: what it is, how it was made, how sure. The package is its file: overview, timeline, single shots. Open the page you need, not the whole folder.

## The problem

Breaking down a video produces a lot: per-shot measurements, probabilities for how each shot was made, evidence, subtitle timings, sound effect positions, remake prompts, frames, audio stems. Three kinds of readers want different things from it:

| Reader | Wants | Struggles with |
|---|---|---|
| People | The verdict, what makes it work, steps to remake it | Scattered, technical detail |
| Models and agents | The facts that answer the user's question | Context cost, getting lost in detail, mistaking inference for fact |
| Programs | Stable fields and values | Formats that change silently, parsing prose |

People get a report. Programs get raw data. Models had nothing made for them.

Handing a model the raw data does not work. A three-minute talking-head video comes to about 190k tokens of JSON; a 75-shot film recap to about 240k. Reading it for every question is slow and expensive, and measurements, inferences and verdicts sit side by side, so "the tools think this is 41% likely a screen recording" turns into "this is a screen recording".

Handing a model the human report does not work either. It is written for reading top to bottom, with folds and narrative, and there is no stable structure to read only part of it.

VIDEO.md is the format for that missing reader.

## Where the ideas come from

Nothing in VIDEO.md is new. It combines a few things that already work.

### Agent Skills: progressive disclosure

A skill is a folder. The `name` and `description` in the front matter of `SKILL.md` stay in the agent's context, a few dozen tokens. The agent reads the body only when the skill is relevant; the body points to files under `references/`, opened only when needed.

VIDEO.md uses the same structure, with a video in place of a capability:

| Agent Skill | VIDEO.md |
|---|---|
| `SKILL.md` front matter: name, description | `VIDEO.md` front matter: the card (name, description, method mix, confidence) |
| `SKILL.md` body: instructions | `VIDEO.md` body: verdict, open questions, map |
| `references/*.md`, opened on demand | `video/*.md`, one topic each, opened on demand |
| Scripts and assets | Raw data, frames, audio stems |

It goes one step further: every file states its size in tokens, and so does the map. A skill tells the agent what is there; VIDEO.md also tells it what opening it costs, so the model can weigh that before reading.

### A small DSL: one line per shot

The timeline is the spine of the package. It is not a JSON array or a Markdown table but a small line format:

```
#07 16.2-18.5 | seen man talking, chat screenshots pop up | camera static | made~ screen capture 41% | flag low confidence
```

The idea is the same as SRT subtitles, EDL edit lists or log lines: one record per line, number and time first, then `key value` pairs. Why:

- **Dense.** The same data as JSON spends much of its tokens on keys, quotes and brackets. A 75-shot timeline is about 3.5k tokens; a model can read the whole video at once.
- **Readable as is.** People and models read it without rendering, and models write it without mistakes.
- **Easy to parse.** Three rules: the head is `#n start-end`, fields are separated by ` | `, the key is everything before the first space. Values never contain `|`. The reference parser is a dozen lines.
- **Inference is in the syntax.** A key ending in `~` (`made~`, `material~`) is inferred; a key without it is seen or measured. Readers do not need to work it out from context.

The DSL is used only there. Cards and shot data are YAML front matter checked by a JSON Schema; explanations are plain Markdown. The compact syntax goes where density matters most, and everywhere else uses formats everyone already reads.

### Also

- **Markdown with YAML front matter**, as in static site generators and Agent Skills: the body for models, the front matter for programs, one file for both.
- **JSON Schema** for every front matter, so `videomd check` can validate a package.
- **A directory is the package**, as with skills: no archive format and no index database. Copy it, zip it, commit it.

The map in `VIDEO.md` uses the same line format as the timeline (`path | tokens | about`), so a package has one small grammar, not two.

## Decisions

### A small required core

A card needs six fields: version, name, description, source, number of shots, language. A shot needs its number and time. Everything else is optional, including the judgement of how each shot was made.

Skills work the same way: only `name` and `description` are required. A tool that only summarises content, or a creator describing their own video, can write a conforming package without inventing data it does not have. A tool that does judge production methods adds `made_mix` and `inferred`, and readers that understand them use them.

### An identity

The card is called an ID card, so it carries one: `source.sha256`, the hash of the whole file, and `source.url` when the video came from a link. Two packages written by two tools for the same video can be matched, compared and merged.

### Four levels, each an order of magnitude bigger

| Level | Size | Enough to answer |
|---|---|---|
| L0 card | 100–300 tokens | What it is about, and whether to open it |
| L1 overview and map | 1–2k | The verdict, the remake outline, what is uncertain, which file to read next |
| L2 topics | hundreds to thousands | One aspect in full: timeline, sound, packaging, remake |
| L3 shots | 500–1000 | One shot: what is seen, what is inferred and why, prompts, frames |
| L4 raw | 100k+ | Programs |

Most questions ("how was this made", "what material do I need", "which shots should I check") are answered at L1. Per-shot questions add the timeline, about 4k tokens in total. Only checking a single shot needs L3.

The levels follow how people ask: about the whole video first, then about one aspect, then about one shot.

### The cost is known before reading

Every file has `tokens` in its front matter, and the map has a column for it. It changes how a model reads: not "open it and see" but "is this worth 14k tokens of remake plan, or is the `remake` field in the timeline enough?"

### Seen and inferred are kept apart

This is the most important rule. A breakdown holds two very different kinds of statement:

- **Seen**: a person is talking, there is a title top right, the camera is fixed. Checkable against the frames.
- **Inferred**: this shot is AI-generated (72%), based on its noise and frame rate. Not necessarily checkable by eye.

Mixed together, a model passes inference on as fact and the user cannot tell which sentence to trust. So VIDEO.md separates them three times: `~` keys in the timeline; separate "seen" and "inferred" sections in shot files; and all inferred fields under `inferred`, with a probability, alternatives and `decided_by` (`tools`, `model`, `agent`, `human`). When they disagree, the frames win.

### The timeline is the spine

Video is linear, and nearly every question comes down to "which second, which shot". The timeline is the one L2 file worth reading in full; topic files and shot files hang off it by shot number. Its `flag` field marks the shots that need a look, so a model scanning it knows which frames to open.

### Fixed form, open content

What programs depend on is fixed: front matter fields, the timeline grammar, the taxonomy ids. What can grow is open: new timeline keys, new topic files, new overlay ids, `x-` ids for anything outside the taxonomy. Readers ignore what they do not know. Additions keep the version number; only changing a meaning raises it.

So when a producer gets better (a new dimension of camera work, say), existing readers keep working.

### Prose for models, ids for programs

Timeline values are prose in the package's language: "screen capture 41%" or "屏幕录制 41%", because a model reads them. Stable ids such as `screen_capture` live in the front matter of shot files and in `made_mix`, and programs read only those. Each layer does one job, and neither has to be parsed out of the other.

## What it gives you

**Agents**
- Answering a question costs thousands of tokens instead of hundreds of thousands, so one conversation can cover several videos and many follow-ups.
- No need to know any producer's internal data; reading Markdown is enough.
- Inference is marked, so it is harder to overstate when relaying it to the user.
- The map and token counts let the agent decide how deep to go, instead of following a fixed script.

**Programs**
- A schema, a validator and a reference reader. Programs can rely on front matter and timeline lines alone and never parse prose or raw data.
- New content does not break existing parsers.

**People**
- A package is Markdown; it can be read without any tool.
- Where each verdict came from is recorded (`readers`, `decided_by`): measured, looked at by a model, reviewed by an agent, or corrected by a person.

**The ecosystem**
- Producers and consumers are decoupled. Any breakdown tool that writes a conforming package works with any agent or program that reads one.
- Review has a place to land: flagged shots are marked in the timeline, and when a review is written back the package is regenerated and `decided_by` changes.

## What it is not

- **Not a report.** A report is for people: a story and steps. VIDEO.md is for models: facts and structure. Both can come from the same data.
- **Not an editing interchange format.** EDL and OpenTimelineIO describe how clips assemble into a cut, for editing software. VIDEO.md describes what is in a video and how it was made, for understanding and remaking it.
- **Not a database.** No query language, no index. One video, one directory, found by the map and file names.

## Alternatives

| Approach | Problem |
|---|---|
| Give the model the raw JSON | Too big; measurement, inference and verdict mixed |
| Give the model the report | No stable structure; cannot read part of it |
| Let the model watch the video each time | Slow, costly, not reproducible, and blind to frame rate, noise and metadata |
| One big Markdown file | Too long to read, or too short to be useful; no way to open it up |
| A JSON API only | Fine for programs, wasteful for models, unreadable for people |

VIDEO.md does not pick one of these. It layers them: the top for models, the middle for models and programs, the bottom for programs.
