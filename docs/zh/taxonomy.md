# 取值表

> 本文是 [taxonomy.md](../taxonomy.md) 的中文版，两者不一致时以英文版为准。

VIDEO.md 第 1 版使用的标准 id。不在这些列表里的 id 以 `x-` 开头（见[规范](spec.md)第 9 节）。

## 制作方式

用在 `made_mix` 的键、`inferred.made`、`inferred.alternatives` 的键里。描述的是一个镜头的底层画面怎么做出来的，不包括上面的叠加层。

| id | 含义 |
|---|---|
| `live_action` | 用摄像机拍的实拍 |
| `ai_video` | 视频模型生成 |
| `avatar` | 数字人 |
| `cg_3d` | 3D 渲染 |
| `code_render` | 代码或模板渲染（动态图形、幻灯片、数据图表） |
| `screen_capture` | 录屏或截图 |
| `still_motion` | 静态图片加推拉或平移 |
| `static_hold` | 静态图片，不动 |
| `anim_2d` | 2D 动画 |
| `stop_motion` | 定格动画 |
| `film_footage` | 影视剧片段 |

## 运镜

用在镜头文件的 `camera` 里。

| id | 含义 |
|---|---|
| `static` | 固定机位 |
| `static_with_subject_motion` | 固定机位，主体在动 |
| `planar_zoom_pan` | 整个画面当作平面推拉或平移 |
| `handheld_like` | 手持晃动 |
| `smooth_move` | 平滑运镜（滑轨、稳定器、摇臂） |
| `unknown` | 没有测 |

## 叠加层

用在镜头文件的 `overlays` 里。这个列表是开放的：生成方可以增加不带 `x-` 的 id，读的一方必须接受不认识的 id。

| id | 含义 |
|---|---|
| `subtitle` | 跟着台词走的字幕 |
| `title` | 标题 |
| `label` | 指向某样东西的短文字标注 |
| `styled_text` | 花字：带装饰、带动画、用来强调的文字 |
| `static_graphic` | 叠在上面的静态图形 |
| `layout_template` | 围住画面的版式模板 |
| `animated_sticker` | 动态贴纸 |
| `static_sticker` | 静态贴纸 |
| `pip` | 画中画 |

## 判断来源和 `decided_by`

| id | 含义 |
|---|---|
| `tools` | 只有测量和规则 |
| `model` | 看图或看视频的模型看过这个镜头 |
| `agent` | agent 看过帧图并复核了判断 |
| `human` | 人工纠正或确认过 |

## 标记

| id | 含义 |
|---|---|
| `uncertain` | 现有证据分不开两种制作方式，需要看一眼 |
| `disputed` | 两个判断来源意见不一致 |
| `low_confidence` | 判断的概率偏低 |
