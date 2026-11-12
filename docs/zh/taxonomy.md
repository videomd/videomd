# 取值表

> 本文是 [taxonomy.md](../taxonomy.md) 的中文版，两者不一致时以英文版为准。

VIDEO.md 第 1 版使用的标准 id。不在这些列表里的 id 以 `x-` 开头（见[规范](spec.md)第 14 节）。

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

`camera` 只写一个 id 时用在镜头文件的 `camera` 里，每个画面层的 `camera` 也用它。要写多个运镜动作、载体、方向或时间，就用运镜对象（见下文）。

| id | 含义 |
|---|---|
| `static` | 固定机位 |
| `static_with_subject_motion` | 固定机位，主体在动 |
| `planar_zoom_pan` | 整个画面当作平面推拉或平移 |
| `handheld_like` | 手持晃动 |
| `smooth_move` | 平滑运镜（滑轨、稳定器、摇臂） |
| `unknown` | 没有测 |

## 载体

`camera` 是对象时，用在 `camera.rig` 里。

| id | 含义 |
|---|---|
| `tripod` | 固定在三脚架或支架上 |
| `handheld` | 手持 |
| `gimbal` | 稳定器或斯坦尼康 |
| `dolly` | 轨道上的移动车或滑轨 |
| `crane` | 摇臂或吊臂 |
| `drone` | 航拍无人机 |
| `fpv` | 穿越机（FPV 无人机），贴近目标高速飞行 |
| `vehicle` | 装在汽车、自行车或其他交通工具上 |
| `screen` | 录屏，没有实体摄像机 |
| `virtual` | 虚拟摄像机：3D、游戏引擎、生成视频 |
| `unknown` | 不知道 |

## 运镜动作

用在 `camera.moves` 的 `type` 里。运镜动作可以加 `direction`（`left`、`right`、`up`、`down`、`in`、`out`、`cw`、`ccw`）和 `speed`（`slow`、`medium`、`fast`）。

| id | 含义 |
|---|---|
| `static` | 摄像机不动 |
| `pan` | 原地左右摇 |
| `tilt` | 原地上下摇 |
| `roll` | 旋转（滚转）：绕镜头光轴转（`cw`、`ccw`） |
| `push_in` | 推近主体 |
| `pull_out` | 拉远主体 |
| `truck` | 横移 |
| `pedestal` | 垂直升降 |
| `crane` | 沿弧线升起或落下 |
| `orbit` | 环绕：绕着主体转（`cw`、`ccw`） |
| `follow` | 跟拍移动的主体 |
| `zoom_in` / `zoom_out` | 改变焦距，摄像机位置不动 |
| `crash_zoom` | 急推变焦：极快的变焦 |
| `dolly_zoom` | 希区柯克变焦：边移动边反向变焦，主体大小不变，背景被拉伸 |
| `whip_pan` | 甩镜：左右摇得极快，画面糊掉 |
| `whip_tilt` | 上下摇得极快，画面糊掉 |
| `shake` | 故意晃动，制造冲击感 |
| `handheld_drift` | 手持摄像机轻微的漂移 |
| `planar_zoom_pan` | 整个画面当作平面推拉或平移 |

## 转场

用在 `transition_in.type` 里。

| id | 含义 |
|---|---|
| `cut` | 直接硬切 |
| `jump_cut` | 跳切：同一构图下跳过一段时间 |
| `match_cut` | 匹配剪辑：前后两镜的形状、动作或位置对得上 |
| `dissolve` | 叠化：上一镜渐渐化成下一镜 |
| `fade_in` / `fade_out` / `fade_through` | 从黑场或白场淡入、淡出到黑场或白场、经过黑场或白场过渡 |
| `wipe` | 划像：一条线或一个形状扫过，换掉上一镜、带出下一镜 |
| `slide` | 下一镜滑进来，把上一镜推出去 |
| `whip` | 甩镜转场：甩镜的模糊把上一镜带到下一镜 |
| `zoom` | 用变焦把上一镜带到下一镜 |
| `spin` | 用旋转把上一镜带到下一镜 |
| `mask` | 遮挡转场：有东西从镜头前经过，挡住剪切点 |
| `morph` | 一个画面变形成下一个画面 |
| `flash` | 用闪白盖住剪切点 |
| `glitch` | 用故障风的数字失真效果盖住剪切点 |
| `l_cut` / `j_cut` | 上一镜的声音延续到下一镜的画面上，或者反过来 |

## 画面层角色

用在 `layers` 的 `role` 里。

| id | 含义 |
|---|---|
| `base` | 底下的主画面 |
| `pip` | 画中画：叠在主画面上的小窗口 |
| `split` | 分屏里的一块 |
| `inset` | 嵌在版式里的带框画面，不是浮在上面 |
| `background` | 抠像主体后面的背景，比如绿幕换的背景 |
| `foreground` | 抠出来放在背景前面的主体 |
| `overlay` | 盖住整个画面的一层：纹理、边框、滤镜 |

## 镜头效果

用在 `lens` 里。这个列表是开放的。

| id | 含义 |
|---|---|
| `rack_focus` | 移焦：焦点从一个主体移到另一个 |
| `shallow_focus` | 浅景深，背景虚化 |
| `deep_focus` | 全景深，前后都清楚 |
| `fisheye` | 明显的桶形畸变 |
| `wide` | 广角的感觉 |
| `telephoto` | 长焦的压缩感 |
| `tilt_shift` | 移轴，看起来像微缩模型 |
| `anamorphic` | 变形宽银幕镜头的拉丝光晕和椭圆焦外 |
| `macro` | 微距，极近的特写 |

## 相关视频

用在 `related` 的 `rel` 里。

| id | 这条视频是…… |
|---|---|
| `same_video` | 同一条视频，比如重新上传的 |
| `remake_of` | 对方的翻拍 |
| `part_of` | 对方的一集或一部分 |
| `clip_of` | 从对方剪出来的 |
| `source_of` | 对方剪辑或翻拍所用的原片 |
| `sequel_of` | 对方的续作 |
| `translation_of` | 对方的另一种语言版本 |

## 投影方式

用在 `source.projection` 里：`flat`（默认）、`equirectangular`、`cubemap`、`fisheye`。

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
