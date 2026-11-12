# VIDEO.md 规范

> 本文是 [SPEC.md](../spec.md) 的中文版，两者不一致时以英文版为准。

本文定义 VIDEO.md 拆片包：一个目录，给模型和程序描述一条视频。它是什么、为什么这样设计，见 [README](https://github.com/videomd/videomd/blob/main/README.zh-CN.md) 和 [设计思路](design.md)。怎么写一个包，见 [生成指南](authoring.md)；怎么在 agent 或应用里用，见 [接入指南](integrate.md)。

「必须」「不得」「应当」「可以」对应 RFC 2119 的 MUST、MUST NOT、SHOULD、MAY。

## 1. 层级

一个包逐层读，每一层比上一层更细，也更贵：

| 层 | 在哪 | 一般大小 | 回答什么 |
|---|---|---|---|
| L0 卡片 | `VIDEO.md` 前置信息 | 100–300 token | 视频讲什么，要不要打开 |
| L1 概览和地图 | `VIDEO.md` 正文 | 1–2k token | 结论、待复核的问题、下一步打开哪个文件 |
| L2 场景 | `video/scenes.md` | 一行一个场景 | 长视频用：视频分成哪几段，先于时间线读 |
| L2 主题 | `video/<topic>.md` | 几百到几千 | 某一方面的完整信息；`video/timeline.md` 一行一个镜头 |
| L3 镜头 | `video/shots/<n>.md` | 每个几百 | 某一镜的完整信息 |
| L4 原始 | 目录里的其他内容 | 不限 | 给程序的数据和媒体文件，由生成方定义 |

读的一方应当从 L0 开始，只在问题需要时才打开下一层。

## 2. 目录结构

```
<包>/
  VIDEO.md             必须   L0 卡片 + L1 概览和地图
  video/
    scenes.md          可选   L2 一行一个场景，长视频用
    timeline.md        必须   L2 一行一个镜头，或说明时间线已拆分
    timeline/01.md     可选   L2 拆分后时间线的一部分
    content.md         可选   L2 讲什么、结构、台词
    cast.md            可选   L2 角色、场景、道具
    sound.md           可选   L2 人声、音乐、音效、节拍
    look.md            可选   L2 实拍镜头的景别、机位、打光、剪辑
    packaging.md       可选   L2 字幕、花字、贴纸、画中画
    remake.md          可选   L2 怎么复刻
    x-<名字>.md        可选   L2 生成方自定义的主题
    shots/01.md        必须   L3 每个镜头一个文件
    transcript.vtt     可选   L4 谁在什么时候说了什么（WebVTT），卡片里写明时才有
  ...                  可选   L4 生成方自定义：原始数据、帧图、分轨音频、字幕文件
```

- 包里的路径，包括写在包内文件里的路径，必须相对于包根目录，不得以 `/` 开头，也不得包含 `..` 这一段。
- 生成方不应当写没有内容的主题文件。
- 镜头文件按镜头编号命名，至少补零到两位：`01.md`、`02.md`……`120.md`。

## 3. 前置信息

包里每个 `.md` 文件都必须以两行 `---` 之间的 YAML 前置信息开头，每份前置信息都必须写明格式版本：

```yaml
videomd: 1
```

`video/` 下的文件还必须有 `part`（这是哪一部分）和 `tokens`（正文的大致大小）：

```yaml
part: timeline
tokens: 2275
```

`part` 取 `timeline`、`scenes`、`content`、`cast`、`sound`、`look`、`packaging`、`remake`、`shot` 或 `x-<name>`。`tokens` 是估算值，让读的一方打开前就能判断；生成方可以用任何分词器。不需要分词器的算法：ASCII 字符数 ÷ 4 + 其他字符数 × 0.75。

每种前置信息的字段由 [schema/videomd-1.schema.json](https://github.com/videomd/videomd/blob/main/schema/videomd-1.schema.json)（JSON Schema 2020-12）定义：`VIDEO.md` 对应 `card`，主题文件对应 `part`，镜头文件对应 `shot`。前置信息可以带 schema 没有定义的字段。

## 4. 卡片（L0）

`VIDEO.md` 的前置信息。最小的卡片：

```yaml
---
videomd: 1
name: city-walk
description: 黄昏城市漫步，两个镜头，从路口走到一家亮着灯的店面。
source: {file: city-walk.mp4, duration: 8.0}
shots: 2
lang: zh
---
```

字段齐全的卡片：

```yaml
---
videomd: 1
name: coffee-ad
description: >-
  一条 10 秒的咖啡广告：一只手往玻璃杯里倒咖啡，然后一张卡片显示价格。
  实拍的产品镜头（70%）加代码渲染的价格卡（30%）。
source:
  file: coffee-ad.mp4
  url: https://example.com/videos/coffee-ad
  sha256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
  duration: 10.0
  size: 1080x1920
  fps: 30.0
  aspect: '9:16'
shots: 2
lang: zh
made_mix: {live_action: 0.7, code_render: 0.3}
confidence: 0.84
readers: [tools, model]
open_questions: 1
generator: {name: rea-video, version: 0.1.0}
---
```

长视频或有相关视频的，卡片还可以带 `scenes`、`tracks`、`related` 和 `source.projection`：

```yaml
scenes: 2
tracks: {transcript: video/transcript.vtt}
related:
  - {rel: part_of, name: harbour-stories}
  - {rel: remake_of, url: https://example.com/films/harbour-1962}
source: {file: harbour-night.mp4, duration: 300.0, projection: flat}
```

| 字段 | 必须 | 含义 |
|---|---|---|
| `videomd` | 是 | 格式版本：`1` |
| `name` | 是 | 1–64 个字符：小写字母、数字和连字符；不能以连字符开头或结尾，不能有连续两个连字符 |
| `description` | 是 | 1–1024 个字符。先写视频讲什么，再写怎么做的。见下文 |
| `source` | 是 | `duration`（秒），以及 `file` 和 `url` 至少一个 |
| `source.sha256` | 否 | 整个源文件的 SHA-256（十六进制）。跨包、跨生成方识别同一条视频 |
| `source.size`、`fps`、`aspect` | 否 | `宽x高`、帧率、画面比例（如 `'9:16'`） |
| `shots` | 是 | 镜头数，等于时间线行数 |
| `lang` | 是 | 写给模型读的文字所用的语言（BCP 47），如 `en`、`zh`、`pt-BR` |
| `made_mix` | 否 | 制作方式 id（[取值表](taxonomy.md)）到它占时长的比例 |
| `confidence` | 否 | 0–1，整体判断有多确定 |
| `readers` | 否 | 谁参与了判断：`tools`、`model`、`agent`、`human` |
| `open_questions` | 否 | 需要复核的点有几处 |
| `generator` | 否 | 生成方的 `name` 和 `version` |
| `source.projection` | 否 | 投影方式：`flat`（默认）、`equirectangular`、`cubemap` 或 `fisheye`，用于 360° 和 VR 视频 |
| `scenes` | 否 | 场景数，等于 `video/scenes.md` 的行数（第 9 节） |
| `tracks` | 否 | 标准轨道的路径。`transcript`：一个 WebVTT 文件（第 13 节） |
| `related` | 否 | 和这条视频相关的其他视频（第 13 节） |

**description** 是 agent 用来判断这个包能不能回答某个问题的依据，往往要在很多包里挑，而且不打开别的文件。它应当先说视频展示或讲了什么，知道的话再说怎么做的。它应当写得够具体，能和相似的视频区分开。

好的写法：`一条 66 秒的 3D 毛绒动物科普，分四步讲咸鸭蛋为什么会流油。全片 3D 渲染，带字幕和素材库音乐。`
差的写法：`3D 渲染 100%`（只说了怎么做，没说是什么），或 `一个视频`（什么都没说）。

## 5. 概览和地图（L1）

`VIDEO.md` 的正文是写给模型读的 Markdown。应当依次包含：视频讲了什么和结论、待复核的问题、地图、一段简短的读法说明。

地图必须是一个信息字符串为 `videomd-map` 的代码块。每行列一个路径：

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

- 不是匹配模式的路径必须存在；目录路径必须是目录。每个匹配模式必须至少匹配一个文件。匹配模式的 `tokens` 按单个文件计。
- `video/` 下直接放着的每个 `.md` 文件都必须被地图覆盖。
- 生成方应当把包含的 L4 数据列出来，让读的一方知道有这些东西。

## 6. 看到的和推断的

包里始终把两类内容分开：

- **看到的**：看得到、听得到、能对着帧图核实的内容（画面里有什么、运镜、叠加层、文字），以及直接测得的量。
- **推断的**：关于视频怎么做的、素材从哪来的判断，附概率和依据。依据可以是人眼看不出的测量（帧率、噪声、转码、元数据）。

时间线里，键名以 `~` 结尾的是推断的，不带 `~` 的是看到的或测得的。镜头文件里，推断的字段放在 `inferred` 下，正文应当把看到的和推断的分成不同的小节。两者对不上时，以帧图为准。

## 7. 时间线（L2）

时间线列出所有镜头，一行一个，放在信息字符串为 `videomd-timeline` 的代码块里：

```
#07 16.2-18.5 | seen 男子讲话，画面上弹出聊天截图 | camera 固定 | made~ 录屏 41% · 次选 代码渲染 29% | flag 低置信
```

```
line   = head *( " | " field )
head   = "#" number " " seconds "-" seconds
field  = key [ "~" ] " " value
key    = a lowercase letter, then lowercase letters, digits, "_" or "-"
value  = one or more characters, none of them "|"
```

- 镜头编号必须严格递增。结束时间不得早于开始时间。时间是从视频开头算起的秒数。
- 值里不得出现 `|`；生成方要替换掉，比如换成 `/`。
- 键应当按下表顺序出现。没内容的键省略。只有行首是必须的。

| 键 | 含义 | 类别 |
|---|---|---|
| `story` | 这一镜在叙事里的作用和讲的点 | 看到的 |
| `seen` | 画面里有什么，一句话 | 看到的 |
| `layers` | 多画面合成时，每个画面层是什么、在哪（第 11 节） | 看到的 |
| `camera` | 运镜，可以按顺序写多个运镜动作：`orbit, then whip pan right`（第 12 节） | 测得的 |
| `transition` | 和上一镜怎么接，不是直接硬切时才写（第 12 节） | 测得的 |
| `overlay` | 叠加层：字幕、标题、贴纸…… | 测得的 |
| `made~` | 这一镜怎么做的，附概率；` · ` 后面可以跟次选 | 推断的 |
| `material~` | 素材从哪来：生成的、创作者自己拍的、素材库…… | 推断的 |
| `remake` | 怎么复刻这一镜 | 方案 |
| `flag` | 为什么需要复核 | — |
| `x-<name>` | 生成方自定义 | 不限 |

时间线的值是写给模型读的文字，用包的 `lang` 写。程序要用稳定的值，就读镜头文件。

**时间线放在哪。** 大多数视频的代码块就放在 `video/timeline.md`。长视频可以把它拆成几部分：`video/timeline/01.md`、`02.md`……，通常一个场景一部分。这时每部分都有 `part: timeline`、自己的 `shots` 数和一个 `videomd-timeline` 代码块；`video/timeline.md` 不放代码块，只留前置信息（`shots` 是全片的镜头数）和一段说明时间线怎么拆的文字；各部分按文件名顺序连起来就是时间线。一个包不得既在 `video/timeline.md` 里放代码块，又有拆分的部分。

## 8. 镜头文件（L3）

`video/shots/<n>.md` 描述一个镜头。它的前置信息就是这一镜的数据；只有 `shot`、`time` 和 `tokens` 是必须的：

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

| 字段 | 必须 | 含义 |
|---|---|---|
| `shot` | 是 | 镜头编号；等于文件名里的编号 |
| `time` | 是 | `[开始, 结束]`，单位秒 |
| `camera` | 否 | 运镜 id，或带 `rig` 和 `moves` 的运镜对象（第 12 节） |
| `overlays` | 否 | 叠加层 id（[取值表](taxonomy.md)） |
| `inferred` | 否 | 制作方式的判断。有它时，`made`（制作方式 id）和 `p`（概率）是必须的 |
| `inferred.alternatives` | 否 | 其他制作方式 id 到概率 |
| `inferred.decided_by` | 否 | 最后由谁定的：`tools`、`model`、`agent` 或 `human` |
| `inferred.real_material` | 否 | 这一镜里有没有创作者必须自己拿到的真实素材：实拍、照片、截图 |
| `flags` | 否 | `uncertain`、`disputed`、`low_confidence` |
| `frames` | 否 | 这一镜图片的路径：`sheet`（拼图）、`first`、`last`，或别的名字 |
| `scene` | 否 | 这一镜属于哪个场景（第 9 节） |
| `take`、`beats` | 否 | 同一个长镜头拆成的多个镜头；镜头内部的节点（第 10 节） |
| `layers` | 否 | 多画面合成里的各个画面层（第 11 节） |
| `transition_in`、`speed`、`lens` | 否 | 和上一镜怎么接；慢动作、变速、倒放；镜头和对焦效果（第 12 节） |

正文是写给模型读的 Markdown。应当依次包含：看到的、推断的和依据、怎么复刻这一镜。

## 9. 场景和长视频

一部电影或一场长直播有几百上千个镜头，时间线长到没法一次读完。这样的包应当有 `video/scenes.md`，把视频分成的各段放在信息字符串为 `videomd-scenes` 的代码块里，一行一段：

```
#S01 0.0-120.0 | shots 1-4 | story waiting on the harbour | seen night, lanterns, a moored boat
#S02 120.0-300.0 | shots 5-6 | story the storm and the walk home
```

```
line   = "#S" number " " seconds "-" seconds " | shots " first "-" last *( " | " field )
```

- 前置信息里必须有 `part: scenes` 和 `scenes`（行数）；卡片里有 `scenes` 时，两者必须相同。
- 场景必须按顺序排列，时间线里每个镜头恰好被覆盖一次，不能有空缺，也不能重叠。场景从第一个镜头开始时开始，到最后一个镜头结束时结束。
- 镜头文件可以写 `scene`；写了就必须和 `video/scenes.md` 一致。
- `shots` 后面的字段用时间线的键。这里的「场景」指读的人会去找的任何一段：电影的一场戏、讲座的一章、直播的一个环节。

读长视频时，先读 `video/scenes.md`，再只读问题所在场景的那些时间线行，或那一部分时间线。

## 10. 长镜头

时间线的一行通常是两次剪切之间的一个镜头。长镜头（vlog 边走边拍、直播、一镜到底的 MV、一小时的录屏）可以按内容拆成多行时间线，让每一行仍然只讲一件事。拆出来的这些镜头文件带相同的 `take` 编号；同一个长镜头的各镜必须前后相接，每一镜从上一镜结束的地方开始。

任何镜头内部都可以用 `beats` 标出值得定位的时刻，不必再拆镜头：

```yaml
take: 1
beats:
  - {time: [120.0, 150.0], what: rain starts on the pier}
  - {time: [150.0, 210.0], what: he walks along the sea wall}
```

每个节点都必须落在所属镜头的时间范围内。

## 11. 画面层

多画面合成同时显示几路画面：分屏、画中画、游戏画面上叠摄像头、预告片上叠反应镜头、主讲人抠像叠在幻灯片上。`layers` 描述每一路：

```yaml
layers:
  - {id: trailer, role: base, region: [0, 0, 1, 1], seen: game trailer, made: screen_capture, p: 0.9, real_material: true}
  - {id: webcam, role: pip, region: [0.72, 0.68, 0.26, 0.3], seen: host on a webcam, made: live_action, p: 0.95}
```

| 字段 | 含义 |
|---|---|
| `id` | 必须。在同一镜头内唯一；不同镜头里的同一个 id 是同一路画面 |
| `role` | `base`、`pip`、`split`、`inset`、`background`、`foreground`、`overlay`，或 `x-` id |
| `region` | `[x, y, w, h]`，按画面的比例算，原点在左上角；必须在画面内 |
| `seen` | 这个画面层显示什么 |
| `made`、`p`、`real_material` | 这个画面层的制作方式、概率，以及是不是真实素材（推断的） |
| `camera` | 这个画面层自己的运镜，写法同第 12 节 |

有 `layers` 时，`inferred.made` 仍然描述整个镜头：取占画面最大的那个画面层的制作方式。

## 12. 运镜、转场、速度和镜头效果

**运镜。** `camera` 可以是一个运镜 id（[取值表](taxonomy.md)），也可以是一个对象，写明载体并按顺序列出运镜动作：

```yaml
camera:
  rig: virtual
  moves:
    - {type: orbit, direction: cw, speed: medium, time: [12.0, 19.6]}
    - {type: whip_pan, direction: right, speed: fast, time: [19.6, 20.0]}
```

- `rig` 是承载摄像机的东西：`tripod`、`handheld`、`gimbal`、`dolly`、`crane`、`drone`、`fpv`、`vehicle`、`screen`、`virtual`（3D、游戏、生成视频）、`unknown`。
- 每个运镜动作都有 `type`（[取值表](taxonomy.md)），可以有 `direction`（`left`、`right`、`up`、`down`、`in`、`out`、`cw`、`ccw`）、`speed`（`slow`、`medium`、`fast`）和 `time`；`time` 必须落在镜头内。
- 运镜描述的是画面上看起来的运动，不管是真摄像机还是虚拟摄像机拍的。

**转场。** 和上一镜不是直接硬切时，用 `transition_in` 说明怎么接。`type` 取自取值表（`dissolve`、`wipe`、`whip`、`match_cut`、`morph`、`mask`……）；写了 `time` 的话，它必须跨过这一镜的开始时刻。甩镜转场通常从上一镜的最后几帧就开始了。

```yaml
transition_in: {type: whip, time: [19.6, 20.3]}
```

**速度。** `speed` 描述播放速度：`rate`（1 是正常速度，0.25 是四分之一速，8 是延时摄影）、`ramp`（镜头内变速）、`reverse`（倒放）、`freeze`（定格）。

**镜头效果。** `lens` 列出镜头里能看到的镜头和对焦效果：`rack_focus`、`shallow_focus`、`deep_focus`、`fisheye`、`wide`、`telephoto`、`tilt_shift`、`anamorphic`、`macro`。这个列表是开放的。

## 13. 轨道和相关视频

**台词轨。** 卡片里写了 `tracks.transcript` 时，这个文件必须存在，并且是 WebVTT。说话人应当用声音标签 `<v Name>` 标出来。有了台词轨，程序不用读文字就能查到谁说了什么，模型也能带时间引用台词。

```
WEBVTT

00:00:41.000 --> 00:00:44.000
<v Fisherman>Not tonight, then.
```

**相关视频。** `related` 列出其他视频，每项有一个 `rel`，以及 `sha256`、`url`、`name` 至少一个：

| `rel` | 这条视频是…… |
|---|---|
| `same_video` | 同一条视频，比如重新上传的 |
| `remake_of` | 对方的翻拍 |
| `part_of` | 对方的一集或一部分（系列、播放列表） |
| `clip_of` | 从对方剪出来的 |
| `source_of` | 对方剪辑或翻拍所用的原片 |
| `sequel_of` | 对方的续作 |
| `translation_of` | 对方的另一种语言版本 |

## 14. 扩展

- [取值表](taxonomy.md) 以外的制作方式、运镜、载体、运镜动作、转场、画面层角色、关系、判断来源和标记 id 必须以 `x-` 开头，如 `x-game_capture`。读的一方遇到不认识的 id 当作未知处理。叠加层和镜头效果 id 是开放的，不需要前缀。
- 生成方自定义的主题文件命名为 `video/x-<name>.md`，`part: x-<name>`；自定义的时间线键命名为 `x-<name>`；自定义的轨道在 `tracks` 下用自己的名字。
- 读的一方必须忽略不认识的字段、键、文件和 id，不得因为它们而出错。
- 多个生成方都在用的 `x-` id，是取值表的候选（见 [CONTRIBUTING.md](https://github.com/videomd/videomd/blob/main/CONTRIBUTING.md)）。

## 15. 一致性

一个目录是合格的 VIDEO.md 拆片包，当且仅当：

1. `VIDEO.md` 存在，前置信息符合 schema 里的 `card`。
2. `VIDEO.md` 有 `videomd-map` 代码块；每一行都符合第 5 节的语法；每个路径都相对于包；不是匹配模式的路径都存在；每个匹配模式至少匹配一个文件；`video/` 下直接放着的每个 `.md` 文件和每个时间线部分都被覆盖。
3. `video/` 下直接放着的每个 `.md` 文件和每个时间线部分，前置信息都符合 `part`。
4. 时间线要么是 `video/timeline.md` 里的 `videomd-timeline` 代码块，要么是 `video/timeline/` 下的各部分，不能两者都有；每一行都符合第 7 节的语法；镜头编号严格递增；没有镜头结束得比开始早；行数等于卡片里的 `shots`。
5. 时间线每一行都有同编号的镜头文件，其前置信息符合 `shot`，时间和这一行的误差在 0.06 秒以内。
6. `video/shots/` 下每个镜头文件都有对应的时间线行，文件名里的编号等于它的 `shot`。
7. 镜头文件 `frames` 下的每个路径都相对于包，并且存在。
8. 节点和运镜动作落在所属镜头内；`transition_in.time` 跨过所属镜头的开始时刻；画面层的区域在画面内，画面层 id 在同一镜头内唯一。
9. `take` 相同的镜头前后相接，没有空缺。
10. 如果有 `video/scenes.md`，它有 `videomd-scenes` 代码块，每一行都符合第 9 节的语法，按顺序排列，每个镜头恰好覆盖一次，并且和镜头的时间、`scene` 字段一致；场景数和卡片一致。卡片里有 `scenes` 时，`video/scenes.md` 必须存在。
11. `tracks` 下的每个路径都存在；`tracks.transcript` 是 WebVTT 文件。

生成方必须写出合格的包。检查一个包：

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](https://github.com/videomd/videomd/tree/main/conformance/) 里有合格的包，以及各违反一条规则的包；校验器的实现应当给出相同的结果。

## 16. 版本

`videomd: 1` 是当前版本。增加可选的字段、键、主题文件或取值 id 时版本号不变，读的一方忽略不认识的内容。改变字段的含义、地图或时间线的语法、目录结构时升版本号。
