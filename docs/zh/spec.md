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
| L2 主题 | `video/<topic>.md` | 几百到几千 | 某一方面的完整信息；`video/timeline.md` 一行一个镜头 |
| L3 镜头 | `video/shots/<n>.md` | 每个几百 | 某一镜的完整信息 |
| L4 原始 | 目录里的其他内容 | 不限 | 给程序的数据和媒体文件，由生成方定义 |

读的一方应当从 L0 开始，只在问题需要时才打开下一层。

## 2. 目录结构

```
<包>/
  VIDEO.md             必须   L0 卡片 + L1 概览和地图
  video/
    timeline.md        必须   L2 一行一个镜头
    content.md         可选   L2 讲什么、结构、台词
    cast.md            可选   L2 角色、场景、道具
    sound.md           可选   L2 人声、音乐、音效、节拍
    look.md            可选   L2 实拍镜头的景别、机位、打光、剪辑
    packaging.md       可选   L2 字幕、花字、贴纸、画中画
    remake.md          可选   L2 怎么复刻
    x-<名字>.md        可选   L2 生成方自定义的主题
    shots/01.md        必须   L3 每个镜头一个文件
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

`part` 取 `timeline`、`content`、`cast`、`sound`、`look`、`packaging`、`remake`、`shot` 或 `x-<name>`。`tokens` 是估算值，让读的一方打开前就能判断；生成方可以用任何分词器。不需要分词器的算法：ASCII 字符数 ÷ 4 + 其他字符数 × 0.75。

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

`video/timeline.md` 必须有一个信息字符串为 `videomd-timeline` 的代码块。块里每个非空行是一个镜头：

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
| `camera` | 运镜 | 测得的 |
| `overlay` | 叠加层：字幕、标题、贴纸…… | 测得的 |
| `made~` | 这一镜怎么做的，附概率；` · ` 后面可以跟次选 | 推断的 |
| `material~` | 素材从哪来：生成的、创作者自己拍的、素材库…… | 推断的 |
| `remake` | 怎么复刻这一镜 | 方案 |
| `flag` | 为什么需要复核 | — |
| `x-<name>` | 生成方自定义 | 不限 |

时间线的值是写给模型读的文字，用包的 `lang` 写。程序要用稳定的值，就读镜头文件。

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
| `camera` | 否 | 运镜 id（[取值表](taxonomy.md)） |
| `overlays` | 否 | 叠加层 id（[取值表](taxonomy.md)） |
| `inferred` | 否 | 制作方式的判断。有它时，`made`（制作方式 id）和 `p`（概率）是必须的 |
| `inferred.alternatives` | 否 | 其他制作方式 id 到概率 |
| `inferred.decided_by` | 否 | 最后由谁定的：`tools`、`model`、`agent` 或 `human` |
| `inferred.real_material` | 否 | 这一镜里有没有创作者必须自己拿到的真实素材：实拍、照片、截图 |
| `flags` | 否 | `uncertain`、`disputed`、`low_confidence` |
| `frames` | 否 | 这一镜图片的路径：`sheet`（拼图）、`first`、`last`，或别的名字 |

正文是写给模型读的 Markdown。应当依次包含：看到的、推断的和依据、怎么复刻这一镜。

## 9. 扩展

- [取值表](taxonomy.md) 以外的制作方式、运镜、判断来源和标记 id 必须以 `x-` 开头，如 `x-game_capture`。读的一方遇到不认识的 id 当作未知处理。叠加层 id 是开放的，不需要前缀。
- 生成方自定义的主题文件命名为 `video/x-<name>.md`，`part: x-<name>`；自定义的时间线键命名为 `x-<name>`。
- 读的一方必须忽略不认识的字段、键、文件和 id，不得因为它们而出错。
- 多个生成方都在用的 `x-` id，是取值表的候选（见 [CONTRIBUTING.md](https://github.com/videomd/videomd/blob/main/CONTRIBUTING.md)）。

## 10. 一致性

一个目录是合格的 VIDEO.md 拆片包，当且仅当：

1. `VIDEO.md` 存在，前置信息符合 schema 里的 `card`。
2. `VIDEO.md` 有 `videomd-map` 代码块；每一行都符合第 5 节的语法；每个路径都相对于包；不是匹配模式的路径都存在；每个匹配模式至少匹配一个文件；`video/` 下直接放着的每个 `.md` 文件都被覆盖。
3. `video/` 下直接放着的每个 `.md` 文件，前置信息都符合 `part`。
4. `video/timeline.md` 有 `videomd-timeline` 代码块；每一行都符合第 7 节的语法；镜头编号严格递增；没有镜头结束得比开始早；行数等于卡片里的 `shots`。
5. 时间线每一行都有同编号的镜头文件，其前置信息符合 `shot`，时间和这一行的误差在 0.06 秒以内。
6. `video/shots/` 下每个镜头文件都有对应的时间线行，文件名里的编号等于它的 `shot`。
7. 镜头文件 `frames` 下的每个路径都相对于包，并且存在。

生成方必须写出合格的包。检查一个包：

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](https://github.com/videomd/videomd/tree/main/conformance/) 里有合格的包，以及各违反一条规则的包；校验器的实现应当给出相同的结果。

## 11. 版本

`videomd: 1` 是当前版本。增加可选的字段、键、主题文件或取值 id 时版本号不变，读的一方忽略不认识的内容。改变字段的含义、地图或时间线的语法、目录结构时升版本号。
