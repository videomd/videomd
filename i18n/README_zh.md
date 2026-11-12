# VIDEO.md

**给模型逐层读的视频拆解格式。**

[English](../README.md) · 中文

每个技能有一个 `SKILL.md`，每条视频也有一个 `VIDEO.md`。

一个 `VIDEO.md` 拆片包描述一条视频：讲了什么、每一镜怎么做的、画面里有什么、声音是什么、怎么复刻。它从一张约 150 token 的卡片开始，逐层展开到单个镜头；每个文件都写明自己有多少 token，**看到的**和**推断的**始终分开写。

可以这样理解：卡片是这条视频的身份证，一眼看清它是什么、怎么做的、有多确定；整个包是它的档案，要查哪一层就翻到哪一层，不用整本读完。

```
coffee-ad/
  VIDEO.md            卡片（前置信息）+ 概览和地图
  video/
    timeline.md       一行一个镜头
    sound.md  …       一个主题一个文件
    shots/01.md       某一镜的全部细节
  frames/ …           原始数据和媒体文件，由生成方决定
```

## 长什么样

卡片，在 `VIDEO.md` 开头：

```yaml
---
videomd: 1
name: coffee-ad
description: 混合制作：实拍 70% + 代码渲染的价格卡 30%
source: {file: coffee-ad.mp4, duration: 10.0, size: 1080x1920, fps: 30.0}
shots: 2
made_mix: {live_action: 0.7, code_render: 0.3}
readers: [tools, model]
lang: zh
---
```

时间线，一行一个镜头。键名带 `~` 的是推断，不带的是看到的或测得的：

````
```videomd-timeline
#01 0.0-7.0 | seen 一只手往玻璃杯里倒咖啡 | cam 手持 | made~ 实拍(live_action) 92%
#02 7.0-10.0 | seen 米色卡片上写着价格 | cam 固定 | over 标题 | made~ 代码/模板渲染(code_render) 61% · 次选 录屏 30% | flag 低置信
```
````

## 为什么

一条视频的完整拆解数据动辄几十万 token。模型每回答一个问题都读一遍，又贵又慢，还容易把猜测当事实说出去。用 VIDEO.md：

- **多数问题读卡片和概览就能回答**，约 2k token；加上时间线约 4k token，单个镜头的问题也能答。
- **读之前就知道代价。** 每个文件、地图里每一行都写着 token 数。
- **看到的和推断的分开**：语法里分（`made~`），数据里也分（`inferred`，附概率和 `decided_by`）。
- **程序有稳定的接口**：前置信息有 JSON Schema，时间线一行一镜有固定语法，取值是固定的 id。不认识的字段、键、文件一律忽略，格式可以持续扩展。

设计思路见 [DESIGN_zh.md](DESIGN_zh.md)：借鉴了 Agent Skills 和小型 DSL 的哪些做法，每个决定的理由。

## 文档

- [SPEC_zh.md](SPEC_zh.md)：规范（第 1 版）。以英文版 [SPEC.md](../SPEC.md) 为准
- [TAXONOMY.md](../TAXONOMY.md)：制作方式、运镜、叠加层、判断来源、标记的标准取值
- [DESIGN_zh.md](DESIGN_zh.md)：为什么这样设计
- [schema/videomd-1.schema.json](../schema/videomd-1.schema.json)：所有前置信息的 JSON Schema
- [examples/](../examples/)：完整的拆片包
- [conformance/](../conformance/)：合格的包，以及各违反一条规则的包
- [IMPLEMENTATIONS.md](../IMPLEMENTATIONS.md)：生成和读取 VIDEO.md 的工具

## 检查和读取

```bash
pip install videomd
videomd check path/to/package      # 逐条列出不合格的地方；有问题时退出码为 1
videomd read path/to/package       # 以 JSON 输出卡片、时间线和每镜数据
```

```python
import videomd

errors = videomd.check("path/to/package")
pkg = videomd.read("path/to/package")   # {"card": {...}, "timeline": [...], "shots": {1: {...}}}
```

## 给 agent 的读法

先读 `VIDEO.md`，多数问题到这里就够了。按镜头回答时读 `video/timeline.md`，留意 `flag`。只有核实某一镜时才打开 `video/shots/<编号>.md` 和它 `frames` 里的截图。问到某个主题时，按地图打开对应的主题文件。原始数据留给程序。

## 参与

新字段、新键、新取值的提议欢迎开 issue，见 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 许可

规范和文档使用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；代码、schema 和一致性测试用例使用 [Apache-2.0](../LICENSE)。
