---
videomd: 1
name: coffee-ad
description: Mixed — filmed 70% + code-rendered text card 30%
source: {file: coffee-ad.mp4, duration: 10.0, size: 1080x1920, fps: 30.0, aspect: '9:16'}
shots: 2
confidence: 0.84
made_mix: {live_action: 0.7, code_render: 0.3}
readers: [tools, model]
open_questions: 1
lang: en
generator: {name: hand-written, version: '1'}
---

# coffee-ad.mp4

**Verdict** (inferred): filmed product shot, then a rendered price card.

## Open questions

- Shot 2: rendered card or a phone screen recording? Check the frame.

## Map

| File | What is in it | When to read it | ~tokens |
|---|---|---|---|
| `video/timeline.md` | One line per shot | Which shot does what | 120 |
| `video/shots/01.md … 02.md` | Per-shot detail | Checking one shot | 90 |
| `frames/` | Shot frames | Checking by eye | — |
