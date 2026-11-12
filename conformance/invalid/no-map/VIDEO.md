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
made_mix: {live_action: 0.7, x-game_capture: 0.3}
confidence: 0.84
readers: [tools, model]
open_questions: 1
generator: {name: hand-written, version: '1'}
---

# coffee-ad.mp4

**What it says**: pour shot, then the price.
**Made with** (inferred): filmed 70%, rendered card 30%.

## Open questions

- Shot 2: a rendered card or a phone screen recording? Check `frames/02.jpg`.

## Map

```text
video/timeline.md | 120 | One line per shot · which shot does what, which need a look
video/sound.md | 20 | Music and voice
video/x-brand_safety.md | 12 | Logos and claims
video/shots/*.md | 90 | One file per shot · checking one shot
frames/ | - | Shot frames · checking by eye
```
