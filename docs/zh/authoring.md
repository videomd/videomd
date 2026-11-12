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

- `camera`、`overlays`、`inferred`、`layers` 和 `transition_in` 里用 [取值表](taxonomy.md) 的 id。取值表以外的，用 `x-` id。
- 如果你的工具不判断镜头怎么做的，就不要写 `inferred` 和 `made_mix`。不要拿猜测去填。
- `decided_by` 设为最后拍板的那一方。如果是人改过的，就是 `human`，即使先看过的是模型。
- `frames.sheet` 是最有用的图：一张图里放这一镜的第一帧、中间帧和最后一帧，模型看一张图就能核实一个镜头。

正文依次写：看到的；推断的和依据；怎么复刻这一镜。「24 fps source, no sensor noise, letterboxed」这样的证据，能帮模型和复核的人判断结论对不对。

## 长视频

视频超过几百个镜头时，加上场景，并把时间线拆开：

- 写 `video/scenes.md`，一行一个场景：`#S03 610.0-905.5 | shots 212-298 | story the chase through the market`。场景按顺序把每个镜头覆盖一次。讲座或直播的「场景」就是一章或一个环节。
- 把时间线拆成 `video/timeline/01.md`、`02.md`……，一个场景一部分，`video/timeline.md` 里只留一段说明。每一部分都要在地图里列出来，带上大小。
- 卡片里写 `scenes`，每个镜头文件里写 `scene`。

这样模型先读场景列表（就算是一部长片也只有几千 token），再打开其中一部分时间线。

## 长镜头

一个十分钟甚至一小时的长镜头，对摄像机来说仍是一个镜头，对读的人来说不是。按内容把它拆成多行时间线，每行讲一件事，这些行对应的镜头文件写同一个 `take`。镜头内部读的人应该能找到的时刻，用 `beats` 标出来：产品出现、话题切换、抖包袱。

## 多画面合成

分屏、画中画、游戏画面叠摄像头、反应视频、主讲人抠像这类画面，在 `layers` 下列出每个画面层，写明 `region`、显示的内容，判断了制作方式的话也写上。时间线里用一个简短的 `layers` 值写同样的内容：`layers trailer full frame; webcam inset bottom right`。`inferred.made` 仍然是整个镜头的结论。

## 运镜、转场和速度

- 简单的镜头写一个 id 就够了：`camera: static`。
- 再复杂一点就用运镜对象：先写 `rig`，再按顺序写每个运镜动作的 `type`、`direction`、`speed` 和 `time`。先停住、再向右甩镜、然后跟拍主体的镜头，就是三个运镜动作。
- 不是直接硬切的转场，写在它接入的那一镜里：`transition_in: {type: whip, time: [19.6, 20.3]}`。它的时间可以从上一镜就开始。
- 慢动作、延时、变速和倒放写在 `speed` 下，对焦和镜头效果写在 `lens` 下。
- 描述画面上发生了什么。游戏或生成视频里的虚拟摄像机一样会摇、会环绕；把 `rig` 设为 `virtual`。
- 测出来的写进这些字段；只是猜测的写在正文里，或者附上概率。

## 台词和相关视频

- 有台词稿的话，写成 WebVTT，用 `<v Speaker>` 标签标说话人，并在 `tracks.transcript` 里写明路径。文字版的概述还是放在 `content.md`。
- 如果视频是别的视频的翻拍、其中一集、剪出来的片段，或者是重新上传的，在 `related` 里写明。

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
