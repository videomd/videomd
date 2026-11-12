# VIDEO.md 规范（第 1 版）

> 本文是 [SPEC.md](../SPEC.md) 的中文版，两者不一致时以英文版为准。

本文定义 VIDEO.md 拆片包：一个目录，给模型和程序描述一条视频。设计目标见 [DESIGN_zh.md](DESIGN_zh.md)。

「必须」「不得」「应当」「可以」对应 RFC 2119 的 MUST、MUST NOT、SHOULD、MAY。

## 1. 概览

一个包是一个目录，里面有入口文件 `VIDEO.md` 和文件夹 `video/`。读的时候逐层往下，每一层比上一层更细、也更贵：

| 层 | 在哪 | 一般大小 | 回答什么 |
|---|---|---|---|
| L0 卡片 | `VIDEO.md` 前置信息 | 约 150 token | 这是什么视频、怎么做的、有多确定 |
| L1 概览和地图 | `VIDEO.md` 正文 | 1–2k token | 结论、不确定点、下一步该打开哪个文件 |
| L2 主题 | `video/<主题>.md` | 几百到几千 | 某一方面的完整信息；`video/timeline.md` 一行一镜 |
| L3 镜头 | `video/shots/<编号>.md` | 每个 500–1000 | 某一镜：看得到什么、推断是什么、依据、帧图 |
| L4 原始 | 目录里的其他内容 | 不限 | 给程序的数据和媒体文件，由生成方定义 |

读的一方应当从 L0 开始，只在问题需要时才打开下一层。

## 2. 目录

```
<包>/
  VIDEO.md             L0 卡片（前置信息）+ L1 概览和地图（正文）
  video/
    timeline.md        L2，必须：一行一个镜头
    content.md         L2，可选：讲什么、结构、台词
    cast.md            L2，可选：角色、场景、道具
    sound.md           L2，可选：人声、音乐、音效、节拍
    look.md            L2，可选：实拍镜头的景别、机位、打光、剪辑
    packaging.md       L2，可选：字幕、花字、贴纸、画中画
    remake.md          L2，可选：怎么复刻
    x-<名字>.md        L2，可选：生成方自定义的主题
    shots/01.md        L3，必须：每个镜头一个文件
  ...                  L4，可选：生成方自定义（原始数据、帧图、分轨音频、字幕文件）
```

- 包里所有路径，包括写在 `video/` 下文件里的路径，都必须相对包根目录，不得以 `/` 开头，不得包含 `../`。
- 没有内容的主题文件不应当生成。
- 镜头文件按镜头编号命名，至少补零到两位：`01.md`、`02.md`……`120.md`。

## 3. 前置信息

包里每个 `.md` 文件都必须以两行 `---` 之间的 YAML 前置信息开头，并且必须写明格式版本：

```yaml
videomd: 1
```

`video/` 下的文件还必须有：

```yaml
part: timeline   # 这是哪一部分：timeline、content、cast、sound、look、packaging、remake、shot，或 x-<名字>
tokens: 2275     # 正文大约多少 token
```

`tokens` 是估算值，让读的一方在打开前就能权衡。生成方可以用任何分词器；不依赖分词器的算法是：ASCII 字符数 ÷ 4 + 其他字符数 × 0.75。

每种前置信息的完整字段见 [schema/videomd-1.schema.json](../schema/videomd-1.schema.json)（JSON Schema 2020-12）：`VIDEO.md` 对应 `card`，主题文件对应 `part`，镜头文件对应 `shot`。

## 4. 卡片（L0）

`VIDEO.md` 的前置信息：

```yaml
videomd: 1
name: coffee-ad
description: 混合制作：实拍 70% + 代码渲染的价格卡 30%
source: {file: coffee-ad.mp4, duration: 10.0, size: 1080x1920, fps: 30.0, aspect: '9:16'}
shots: 2
confidence: 0.84                              # 按时长加权的判断置信度
made_mix: {live_action: 0.7, code_render: 0.3}   # 推断，按时长占比
readers: [tools, model]                       # 谁参与了判断
open_questions: 1
lang: zh
generator: {name: rea-video, version: 0.1.0}
```

| 字段 | 必须 | 含义 |
|---|---|---|
| `videomd` | 是 | 格式版本，`1` |
| `name` | 是 | 视频的简短名字 |
| `description` | 是 | 一句话，不超过 200 字符：是什么、怎么做的 |
| `source` | 是 | 必须有 `file` 和 `duration`（秒）；`url`、`size`（`宽x高`）、`fps`、`aspect` 可选 |
| `shots` | 是 | 镜头数，等于时间线行数 |
| `made_mix` | 是 | 制作方式（见 [TAXONOMY.md](../TAXONOMY.md)）到时长占比 |
| `lang` | 是 | 写给模型读的文字所用的语言，如 `en`、`zh` |
| `confidence` | 否 | 0–1 |
| `readers` | 否 | `tools`（工具测量）、`model`（看图或看视频的模型）、`agent`（看过帧图的 agent）、`human`（人） |
| `open_questions` | 否 | 需要复核的点有几处 |
| `generator` | 否 | 生成方的 `name` 和 `version` |

## 5. 概览和地图（L1）

`VIDEO.md` 的正文是给模型读的 Markdown，格式不限。应当依次包含：结论、不确定点、地图、简短的读法说明。

地图是一张 Markdown 表格，每行以反引号括起的路径开头：

```
| 文件 | 里面有什么 | 什么时候读 | 约 token |
|---|---|---|---|
| `video/timeline.md` | 一行一个镜头 | 想知道哪镜做了什么 | 2049 |
| `video/shots/01.md … 21.md` | 逐镜细节 | 核实某一镜 | 570 |
| `shots/, stems/` | 帧图、分轨音频 | 看图核实 | — |
```

路径里有 `…` 的行表示一组文件，有 `,` 的行列出多个路径。其余每行的路径都必须存在。

## 6. 看到的和推断的

包里始终把两类信息分开：

- **看到的**：看得到、听得到、能对着帧图核实的内容（画面里有什么、运镜、叠加层、文字），以及直接测得的量。
- **推断的**：关于制作方式和素材来源的判断，附概率和依据。依据可能是肉眼看不出的测量（帧率、噪声、转码、元数据）。

时间线里，键名后带 `~` 的是推断，不带的是看到的或测得的。镜头文件里，推断的字段放在 `inferred` 下，正文应当把「看到的」和「推断的」分成两节。两者对不上时，以帧图为准。

## 7. 时间线（L2）

`video/timeline.md` 必须有且只有一个信息字符串为 `videomd-timeline` 的代码块。块里每个非空行是一个镜头：

```
#07 16.2-18.5 | seen 男子讲话，画面上弹出多张聊天截图 | cam 固定 | made~ 屏幕录制/截图(screen_capture) 41% · 次选 代码渲染 29% | flag 低置信
```

语法：

```
行     = 行首 *( " | " 字段 )
行首   = "#" 编号 " " 秒 "-" 秒
字段   = 键 [ "~" ] " " 值
键     = 小写字母 *( 小写字母 / 数字 / "_" / "-" )
值     = 一个或多个字符，不含 "|"
```

- 镜头编号必须严格递增，结束时间不得早于开始时间。
- 值里不得出现 `|`，生成方要替换掉，比如换成 `/`。
- 键应当按下表顺序出现，没有的键省略。

| 键 | 含义 | 类别 |
|---|---|---|
| `say` | 这一镜在叙事里的作用和讲的点 | 看到的 |
| `seen` | 画面里有什么，一句话 | 看到的 |
| `cam` | 运镜 | 测得的 |
| `over` | 叠加层：字幕、标题、贴纸…… | 测得的 |
| `made~` | 制作方式和概率。括号里必须是 [TAXONOMY.md](../TAXONOMY.md) 里的类别 id；` · ` 之后可以跟次选 | 推断 |
| `real~` | 素材来源：生成的、创作者自己的素材、混合…… | 推断 |
| `remake` | 复刻路线 | 方案 |
| `flag` | 为什么需要复核 | — |

值是写给模型读的，跟着包的 `lang` 走。程序要用稳定的值，就读镜头文件，或者取 `made~` 括号里的 id。

读的一方遇到不认识的键必须忽略。以后的修订可以增加新键。

## 8. 镜头文件（L3）

`video/shots/<编号>.md` 描述一个镜头，前置信息是这一镜的结构化数据：

```yaml
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
```

| 字段 | 必须 | 含义 |
|---|---|---|
| `shot`、`time` | 是 | 镜头编号和 `[开始, 结束]`（秒） |
| `inferred.made`、`inferred.p` | 是 | 制作方式 id 和概率 |
| `inferred.alternatives` | 否 | 其他制作方式 id 到概率 |
| `inferred.decided_by` | 否 | 最后由谁定的：`tools`、`model`、`agent` 或 `human` |
| `inferred.real_material` | 否 | 这一镜里有没有创作者必须自己拿到的真实素材（实拍、照片、截图） |
| `camera` | 否 | 运镜 id（见 [TAXONOMY.md](../TAXONOMY.md)） |
| `overlays` | 否 | 叠加层 id（见 [TAXONOMY.md](../TAXONOMY.md)） |
| `flags` | 否 | `uncertain`、`disputed`、`low_confidence` |
| `frames` | 否 | `sheet`、`first`、`last`：这一镜帧图的路径 |

正文是 Markdown，格式不限，应当依次包含：看到的、推断的和依据、怎么复刻这一镜。

## 9. 扩展

- [TAXONOMY.md](../TAXONOMY.md) 以外的制作方式、运镜、判断来源、标记 id 必须以 `x-` 开头，如 `x-game_capture`。读的一方遇到不认识的 id 时当作未知处理。
- 生成方自定义的主题文件命名为 `video/x-<名字>.md`，`part: x-<名字>`。
- 任何前置信息都可以带 schema 里没有的字段。读的一方遇到不认识的字段、键、文件必须忽略。
- 多个生成方都在用的 `x-` id，是下一版取值表的候选。

## 10. 一致性要求

一个目录是合格的 VIDEO.md 拆片包，当且仅当：

1. `VIDEO.md` 存在，前置信息符合 schema 里的 `card`。
2. `VIDEO.md` 地图里列出的每个路径都存在（带 `…` 或 `,` 的行除外）。
3. `video/` 下每个 `.md` 文件的前置信息符合 `part`。
4. `video/timeline.md` 有 `videomd-timeline` 代码块；块里每一行都符合第 7 节的语法；编号严格递增；结束时间不早于开始时间；行数等于卡片里的 `shots`。
5. 时间线每一行都有同编号的镜头文件，前置信息符合 `shot`；编号和时间与时间线一致（允许 0.06 秒误差）；`made~` 括号里的 id 等于 `inferred.made`。
6. 镜头文件 `frames` 里的每个路径都存在。

生成方写出的包必须合格。读的一方不得因为不认识的内容而报错。

检查一个包：

```bash
pip install videomd
videomd check path/to/package
```

[conformance/](../conformance/) 里有合格的包，以及各违反一条规则的包。

## 11. 版本

`videomd: 1` 是当前版本。增加字段、键、主题文件或取值 id 时版本号不变，读的一方忽略不认识的内容；改变已有字段的含义、时间线语法或目录结构时升版本号。
