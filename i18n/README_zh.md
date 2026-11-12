# VIDEO.md

**给模型逐层读的视频拆解开放格式。**

**[videomd.github.io/videomd/zh](https://videomd.github.io/videomd/zh/)** · [English](../README.md) · 中文

每个技能有一个 `SKILL.md`，每条视频也有一个 `VIDEO.md`。

可以这样理解：卡片是这条视频的身份证，一眼看清它是什么、怎么做的、有多确定；整个包是它的档案，要查哪一层就翻到哪一层，不用整本读完。

一个 VIDEO.md 拆片包给 AI agent 和程序描述一条视频：逐镜讲了什么、画面里有什么；生成方知道的话，还有每一镜是怎么做的、怎么复刻。它从一张小卡片开始，逐层展开，直到单个镜头。每个文件都写明自己有多少 token，**看到的**和**推断的**分开写。

> **状态**：第 1 版，草案。正式定稿前格式还可能变，见 [CHANGELOG.md](../CHANGELOG.md)。

## 一个包长什么样

```
coffee-ad/
  VIDEO.md            卡片 + 概览和地图          先读
  video/
    timeline.md       一行一个镜头               问到具体镜头时读
    sound.md  …       一个主题一个文件           问到这个主题时读
    shots/01.md       某一镜的全部细节           核实某一镜时读
  frames/ …           原始数据和媒体文件         给程序和看图模型
```

卡片在 `VIDEO.md` 开头。agent 只看它就能决定要不要打开这个包：

```yaml
---
videomd: 1
name: coffee-ad
description: >-
  一条 10 秒的咖啡广告：一只手往玻璃杯里倒咖啡，然后一张卡片显示价格。
  实拍的产品镜头（70%）加代码渲染的价格卡（30%）。
source: {file: coffee-ad.mp4, sha256: 9f86d0…, duration: 10.0}
shots: 2
lang: zh
---
```

时间线一行一个镜头。键名以 `~` 结尾的是推断的，其他的是看到的或测得的：

```
#01 0.0-7.0 | seen 一只手往玻璃杯里倒咖啡 | camera 手持 | made~ 实拍 92%
#02 7.0-10.0 | seen 米色卡片上写着价格 | overlay 标题 | made~ 代码渲染 61% · 次选 录屏 30% | flag 低置信
```

## 为什么

一条视频的完整拆解动辄几十万 token。模型每回答一个问题都读一遍，又慢又贵，还容易把猜测当事实复述。用 VIDEO.md：

- **agent 可以同时知道很多条视频。** 每张卡片几百 token，都放在上下文里，用到时才打开对应的包，和技能一样。
- **多数问题读概览就能回答**，约 2k token。加上时间线约 4k，单个镜头的问题也能答。
- **读之前就知道代价。** 地图列出每个文件和它的 token 数。
- **看到的和推断的分开**：语法里分（`made~`），数据里也分（`inferred`，附概率和由谁判定）。
- **程序有稳定的接口**：前置信息有 JSON Schema 校验，时间线一行一镜有固定语法，id 固定。不认识的字段、键、文件一律忽略，格式可以持续扩展。
- **起步很小。** 六个字段就是一张合格的卡片。判断视频怎么做的是可选模块，不是必需的。

## 文档

| | |
|---|---|
| [SPEC_zh.md](SPEC_zh.md) | 规范 |
| [integrate_zh.md](integrate_zh.md) | 在 agent 或应用里用拆片包：发现、上下文、加载、如实回答 |
| [authoring_zh.md](authoring_zh.md) | 写拆片包：从最小的合格包到完整的包 |
| [design_zh.md](design_zh.md) | 为什么这样设计：借鉴了 Agent Skills 和小型 DSL 的哪些做法 |
| [TAXONOMY.md](../TAXONOMY.md) | 标准 id：制作方式、运镜、叠加层、判断来源、标记 |
| [schema/](../schema/videomd-1.schema.json) | 所有前置信息的 JSON Schema |
| [examples/](https://github.com/videomd/videomd/tree/main/examples/) | 完整的拆片包 |
| [conformance/](https://github.com/videomd/videomd/tree/main/conformance/) | 合格的包，以及各违反一条规则的包 |
| [IMPLEMENTATIONS.md](../IMPLEMENTATIONS.md) | 生成和读取 VIDEO.md 的工具 |

## 检查和读取一个包

```bash
pip install videomd
videomd check path/to/package      # 逐条列出不合格的地方；有问题时退出码为 1
videomd read path/to/package       # 以 JSON 输出卡片、地图、时间线和每镜数据
```

```python
import videomd

errors = videomd.check("path/to/package")
pkg = videomd.read("path/to/package")   # {"card": {...}, "map": [...], "timeline": [...], "shots": {1: {...}}}
```

## 参与

欢迎开 issue 提议新字段、新键和新的取值 id，见 [CONTRIBUTING.md](../CONTRIBUTING.md)。如果你做了生成或读取 VIDEO.md 的工具，请加到 [IMPLEMENTATIONS.md](../IMPLEMENTATIONS.md)。

## 许可

规范和文档使用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，代码、schema 和一致性测试文件使用 [Apache-2.0](https://github.com/videomd/videomd/blob/main/LICENSE)。
