# 编写 VIDEO.md 拆片包

这篇写给开发视频拆解工具的人，以及手写拆片包的人。它从最小的合格包讲到完整的包，说明每一部分怎么写，模型才用得好。规则在 [规范](spec.md) 里；这一页讲怎么写好。

## 最小的拆片包

四个文件。[conformance/valid/minimal](https://github.com/videomd/videomd/tree/main/conformance/valid/minimal/) 就是这个包。

`VIDEO.md`：

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

`video/timeline.md`：

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

`video/shots/01.md`（`02.md` 同理）：

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

检查一下：

```bash
pip install videomd
videomd check city-walk/
```

其他都是可选的。你的工具知道什么，就加什么。

## 卡片

**`name`**：由文件名或标题转成的 slug，小写，用连字符：`salted-egg`，不要 `Salted_Egg final(2)`。

**`description`**：agent 不打开任何文件、要在多条视频里挑出这一条时读的那一行。先说视频展示或讲了什么，知道的话再说怎么做的：

- 好的写法：`A 66-second 3D plush-animal explainer on why salted duck eggs ooze oil, in four steps. Fully 3D rendered, with subtitles and stock music.`
- 差的写法：`3D render 100%`，只说了怎么做，没说是什么；或者 `final.mp4`。

**`source`**：只要手上有文件，就给出整个文件的 `sha256`。两个工具写的两个包是不是描述同一条视频，就靠它判断。视频来自链接时，给出 `url`。

**`lang`**：你的文字用的语言。所有文字用同一种语言写。

## 时间线

一行一个镜头，而且这是模型可能整个读完的唯一一个 L2 文件，所以每行要短：`seen` 写一句话，其他的写几个词。一条 75 镜的视频也应当控制在约 4k token 以内。

- **镜头。** 通常是两次剪切之间的一个镜头。剪切很多的长视频，分段粗一些也可以，只要每一秒都属于某一行，并且镜头文件对得上。
- **看到的键**（`story`、`seen`、`camera`、`overlay`）描述任何人看了都能核实的东西。不要在里面写判断。
- **推断的键**（`made~`、`material~`）写判断，附概率：`made~ AI video 72% · runner-up filmed 20%`。
- **`flag`** 标出复核的人应该看的镜头，并说明原因：置信度低、两个判断来源意见不一、证据分不清两种制作方式。模型扫时间线时会先看这些行，所以只标重要的，别的不要标。
- 值里的 `|` 一律换成 `/`。

## 镜头文件

前置信息给程序，正文给模型。

- `camera`、`overlays` 和 `inferred` 里用 [取值表](taxonomy.md) 的 id。取值表以外的，用 `x-` id。
- 如果你的工具不判断镜头怎么做的，就不要写 `inferred` 和 `made_mix`。不要拿猜测去填。
- `decided_by` 设为最后拍板的那一方。如果是人改过的，就是 `human`，即使先看过的是模型。
- `frames.sheet` 是最有用的图：一张图里放这一镜的第一帧、中间帧和最后一帧，模型看一张图就能核实一个镜头。

正文依次写：看到的；推断的和依据；怎么复刻这一镜。「24 fps source, no sensor noise, letterboxed」这样的证据，能帮模型和复核的人判断结论对不对。

## 主题文件

有话可说才写。每个文件以标题开头，直接进入内容：不要折叠，不要 HTML，不要内嵌图片（图片路径放在镜头文件的 `frames` 里，或者放进地图）。

生成方专用的主题是 `video/x-<name>.md`。

## 概览和地图

`VIDEO.md` 的正文是大多数问题的答案来源。按模型需要的顺序来写：视频讲了什么、结论、复刻概要、待复核的问题，最后是地图。

地图里：

- 列出每个主题文件和镜头文件（写成 `video/shots/*.md`）。
- 写真实的 token 数；模型靠它决定打开什么。
- 写什么时候该读这个文件，不只写里面有什么：`Sound · voice, music, effects, beats and where they came from`。
- 列出你包含的 L4 数据，token 写 `-`。

## token 数

用任何分词器数每个文件的正文，或者用规范里的算法：ASCII 字符数 ÷ 4 + 其他字符数 × 0.75。大致准确就行，不用精确。

## 发布之前

- `videomd check` 通过。
- description 说清了视频讲什么。
- 看到的和推断的没有混在一起：`seen` 里没有判断，每个 `~` 值都有概率。
- 标记指向的是需要复核的镜头。
- 没有隐私信息：任何文件里，包括 L4 数据，都没有本地路径、账号名、API 地址或密钥。

把你的工具加到 [实现列表](implementations.md)。
