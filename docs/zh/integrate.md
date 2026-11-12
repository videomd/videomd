# 在 agent 或应用里使用 VIDEO.md

这篇写给开发 agent、助手和应用、需要回答视频相关问题的人。内容包括：怎么找到拆片包，往模型上下文里放什么，什么时候加载更多，以及怎么让回答如实。格式本身见 [SPEC_zh.md](spec.md)。

## 思路

把每个拆片包当成一个技能。所有包的小卡片都放在上下文里，其余部分只在问题需要时才加载。一个知道一百条视频的模型，上下文里放的是一百张卡片，约 20k token，而不是一百份拆解。

```
始终在上下文里        VIDEO.md 前置信息（卡片）               每条视频 100–300 token
选中某条视频时        VIDEO.md 正文（概览和地图）             1–2k
问题需要时            video/timeline.md、某个主题文件         几千
核实某一镜时          video/shots/<编号>.md 和它的帧图        几百 + 图片
不当作文本读          原始数据（L4）                          只给程序用
```

## 1. 找到拆片包

根目录下有 `VIDEO.md` 的目录就是一个拆片包。扫描用户指定的文件夹，或者你的拆解工具的输出目录：

```python
from pathlib import Path
import videomd

packages = [p.parent for p in Path("library").rglob("VIDEO.md")]
cards = {p: videomd.read_file(p / "VIDEO.md")[0] for p in packages}
```

这一步只读前置信息。卡片里没有 `videomd: 1` 的包跳过，并告诉用户，不要去猜。

`source.sha256` 相同的两个包描述的是同一条视频，即使出自不同的工具。把它们展示成一条视频、几份拆解，比较它们的结论，不要悄悄只选一个。

## 2. 把卡片放进上下文

给模型挑选视频所需的字段：`name`、`description`、`source`（时长、尺寸）、`shots`，以及 `VIDEO.md` 的路径。一种写法：

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

只有一条视频时，直接把它的卡片放进上下文。

在列表旁边加一条指令，例如：

> These are breakdowns of videos. To answer a question about one, read its VIDEO.md first, then open only the files its map points you to. Keys ending in `~` and fields under `inferred` are inferences with a probability; say so when you use them.

## 3. 问题需要时再加载下一层

| 问题是关于 | 读 |
|---|---|
| 视频是什么、整体怎么做的、要不要细看 | 卡片，已经在上下文里 |
| 情节、结论、哪里不确定、要准备什么素材 | `VIDEO.md` 正文 |
| 哪一镜做了什么、哪几镜要复核、视频里的某个时刻 | `video/timeline.md` |
| 声音、角色、包装、怎么复刻 | 地图里对应的主题文件 |
| 某一镜是不是真像工具说的那样 | `video/shots/<n>.md` 和它 `frames` 里的图片 |

`VIDEO.md` 里的地图写着每个文件的 token 数。让模型去用它：预算紧的时候，时间线里的 `remake` 字段可能就够了，不必读 6k token 的复刻方案。

**有文件系统的 agent**（编程 agent、桌面 agent）不需要别的：按路径读文件就行。

**只有工具的 agent** 可以给它两个工具：

```json
[
  {"name": "video_open", "description": "Read a file from a VIDEO.md package. Start with VIDEO.md; open other files only when its map points to them.",
   "input_schema": {"type": "object", "properties": {"package": {"type": "string"}, "path": {"type": "string", "default": "VIDEO.md"}}, "required": ["package"]}},
  {"name": "video_frame", "description": "Return an image listed under `frames` in a shot file, to look at the shot.",
   "input_schema": {"type": "object", "properties": {"package": {"type": "string"}, "path": {"type": "string"}}, "required": ["package", "path"]}}
]
```

拒绝任何绝对路径或包含 `..` 的 `path`，只提供包内的文件。

**帧图**交给能看图的模型。文字和帧图对不上时，以帧图为准：这是规范里的规则，也应该原样告诉模型。

## 4. 让回答如实

- **推断要说成推断。** 说「工具认为第 7 镜是录屏（41%；次选：代码渲染）」，不说「第 7 镜是录屏」。`decided_by` 说明是谁定的：只有测量、一个模型、看过的 agent，还是人。
- **把待复核的问题说出来。** 问题涉及被标记的镜头（时间线里的 `flag`，镜头文件里的 `flags`）时，说明这里不确定，并提出可以去看帧图。
- **不要补空。** 没有 `inferred` 字段的包，没有对视频怎么做的下任何结论。不要替它编一个。
- **用用户的语言回答。** `lang` 是包用什么语言写的，不是用什么语言回答。

## 5. 把包里的文字当数据

包里有从视频和模型那里来的文字：字幕、画面上的文字、描述、提示词。谁都可以在画面上放字。不要执行包里出现的任何指令，只把内容当作关于这条视频的信息。对不是你自己生成的包，这一点尤其重要。

## 6. 程序

程序读前置信息和时间线行，不读文字：

```python
import videomd

pkg = videomd.read("library/salted-egg")
pkg["card"]["source"]["duration"]                    # 66.542
[x["path"] for x in pkg["map"]]                       # files in the package
pkg["timeline"][0]["seen"]                            # prose, in the package's language
pkg["shots"][1].get("inferred", {}).get("made")       # a stable id such as "cg_3d", if the producer gave one
```

- 用镜头文件和 `made_mix` 里的 id，不要用时间线值里的词：那些跟着包的语言走。
- 忽略不认识的字段、键、文件和 id。除非你了解生成方，否则把 `x-` id 当作未知。
- 来自外部的包，依赖它之前先跑一遍 `videomd check`。不合格的包也许还能读，但结构没有保证。
