---
videomd: 1
part: remake
tokens: 5686
---

## 复刻方案

**3D 渲染 21 镜 → 10 个生成单元、10 次 Seedance 2.5 调用**

- 默认引擎 Seedance 2.0（含 Mini / Fast） 不支持一次多镜头，用它要逐镜生成 21 次；这里按 Seedance 2.5 规划（单次 ≤30s、可一次出多镜头），共 10 次
- 分组规则：同场景、硬切相连的 AI 镜头合并为一次生成；单次 ≤30s；单元内连续硬切尽量 ≤8s、最多 10s；在叠化/淡入淡出和换场景处切开
- 声音：模型可以同时生成动作音效和环境声；口播建议单独 TTS 再混进去，方便改文案和卡时间

AI 视频模型能吃这几种输入，每个生成单元下面写了要喂哪些、从哪来：
- **文字提示词**：必需，描述画面、动作、运镜
- **首帧图**：锁住第一帧的构图和主体。不给就是纯文生，构图每次都不一样
- **尾帧图**：再锁住最后一帧，模型只补中间过程。适合单个有运镜或动作的镜头
- **参考图**：商品、人物的样子，让多个镜头里长得一样（提示词里用 `@图片1` 指代）
- **参考视频**：照着学动作、运镜和节奏，不复制画面（`@视频1`）；不是每个模型都支持

### 生成单元

每个单元一次生成。表里是要喂给模型的东西，展开单元看来源和提示词。

| 单元 | 镜头 | 时间 | 时长 | 方式 | 要喂的 | 衔接 |
|---|---|---|---|---|---|---|
| G1 | #1 | 0.0–8.9s | 8.9s | 单镜 | — | — |
| G2 | #2–#3 | 8.9–15.8s | 7.0s | 一次多镜头 | — | 首帧用 G1 的尾帧，接上动作（S05） |
| G3 | #4–#6 | 15.8–24.3s | 8.5s | 一次多镜头 | — | 首帧用 G2 的尾帧，接上动作（S05） |
| G4 | #7–#9 | 24.3–29.5s | 5.1s | 一次多镜头 | — | — |
| G5 | #10 | 29.5–30.6s | 1.2s | 单镜 | — | — |
| G6 | #11–#12 | 30.6–38.0s | 7.4s | 一次多镜头 | — | — |
| G7 | #13 | 38.0–41.6s | 3.5s | 单镜 | — | 首帧用 G6 的尾帧，接上动作（S05） |
| G8 | #14–#16 | 41.6–49.6s | 8.0s | 一次多镜头 | — | — |
| G9 | #17–#18 | 49.6–57.2s | 7.6s | 一次多镜头 | — | 首帧用 G8 的尾帧，接上动作（S05） |
| G10 | #19–#21 | 57.2–66.5s | 9.3s | 一次多镜头 | — | 首帧用 G9 的尾帧，接上动作（S05） |

**G1 · 镜头 #1 · 8.9s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 0.0–8.9s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D卡通风格，黄色毛绒小动物在一个简约的绿色庭院里，面前有一个破开的咸鸭蛋，流出红色的油，柔和光线，居中构图。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。
3D动画，黄色毛绒小动物敲开一个咸鸭蛋，红色的油从蛋黄中涌出，旁边一只棕色毛绒小动物惊讶地看着，固定镜头，柔和光线。
```

英文提示词：

```text
3D animation, a yellow furry little animal cracks open a salted duck egg, red oil gushes out from the yolk, a brown furry little animal watches in surprise nearby, static camera, soft lighting.
```

**G2 · 镜头 #2、#3 · 7.0s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 8.9–15.8s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D卡通风格，三个长着毛绒绒毛发的可爱动物角色站在一个白色的碗周围，碗里放着一个小陶罐。背景是简单的几何山丘形状，纯色背景。柔和的顶光，色彩明快。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–4.8s）：三个毛绒绒的卡通动物角色站在画面中，随后它们突然变成三个白色的毛球，并一起向画面右侧滚出，留下中间的碗和罐子。固定镜头。
镜头2（4.8–7.0s）：固定镜头。画面中央是一个装满白色粉末的木碗。几个带有小眼睛的白色圆球依次从粉末堆中弹跳出来，停留在表面，动作轻快，带有弹性缓冲。
```

英文提示词：

```text
Shot 1 (0.0-4.8s): Three fluffy cartoon animal characters stand in the frame, then they suddenly turn into three white fur balls and roll out to the right side of the frame together, leaving the bowl and pot in the middle. Static camera.
Shot 2 (4.8-7.0s): Static camera. In the center is a wooden bowl filled with white powder. Several small white spheres with tiny eyes pop up sequentially from the powder, resting on the surface with a bouncy, elastic animation.
```

**G3 · 镜头 #4–#6 · 8.5s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 15.8–24.3s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D卡通风格，微距摄影，中央一个棕色圆筒花盆，里面露出白色毛茸茸球体，右侧一只毛茸茸的卡通小猴子探头观看，纯色柔和背景，Blender三维渲染质感，柔光
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–3.8s）：固定平视镜头，3D卡通场景，盆中的毛茸茸物体静止，右侧的小猴玩偶眨动大眼睛注视着它，背景微动微悬浮小螺钉，整体保持平稳纯净的三维渲染动画
镜头2（3.8–5.2s）：3D动画，几粒微小盐粒从右上方飞向鸭蛋模型外壳的气孔，镜头固定。
镜头3（5.2–8.5s）：3D科普动画，摄像机平视固定略向后拉远，桌面左侧为装有白色液体的透明圆柱杯，右侧为黄色半透明液体的圆柱杯，中间悬浮一个带有木质边缘的圆形半透膜模型，几个白色光滑小球从左向右穿过中间的半透膜圆环，运动轨迹流畅匀速。
```

英文提示词：

```text
Shot 1 (0.0-3.8s): Static eye-level shot, 3D cartoon scene, a fluffy white ball inside a brown cup, a cute furry monkey character on the right looking at it and blinking, soft studio lighting, Blender 3D render style.
Shot 2 (3.8-5.2s): 3D animation, tiny salt particles fly from the top right towards a pore on a duck egg model, static camera.
Shot 3 (5.2-8.5s): 3D scientific educational animation, camera slowly pulls back. On a clean desktop, a transparent cylinder with white liquid stands on the left, another cylinder with yellow liquid on the right, and a circular semi-permeable membrane frame suspended in the middle. Small smooth white spheres float and pass smoothly through the membrane from left to right, soft studio lighting.
```

**G4 · 镜头 #7–#9 · 5.1s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 24.3–29.5s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D卡通风格，一个切开的咸鸭蛋特写，半透明的蛋白包裹着完美的正圆形橘黄色蛋黄，边缘有几颗圆形的盐粒，干净的纯色背景，柔和的影棚光照，C4D渲染，极简主义，高品质。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–1.8s）：镜头缓慢向中心的橘黄色蛋黄平稳推进，保持3D卡通质感，光影保持不变。
镜头2（1.8–3.5s）：3D卡通风格，特写镜头，一个切开的咸鸭蛋，中间是完美的橙色球体蛋黄，外面包裹着半透明的蛋白。随着时间推移，蛋黄周围的蛋白中逐渐浮现出蓝色的水滴状粒子特效。镜头保持固定。
镜头3（3.5–5.1s）：固定特写镜头，3D剖面展示蛋黄水分抽取过程，数道半透明浅蓝色箭头从蛋黄表面向外侧流动，蛋黄轻微变硬收敛，保持纯净CG动画质感。
```

英文提示词：

```text
Shot 1 (0.0-1.8s): The camera slowly and steadily pushes in towards the orange egg yolk in the center, maintaining the 3D cartoon texture and consistent lighting.
Shot 2 (1.8-3.5s): 3D cartoon style, close-up shot, a cross-section of a salted duck egg with a perfect orange spherical yolk in the center, surrounded by translucent egg white. Over time, blue water droplet-like particle effects gradually appear in the egg white around the yolk. The camera remains static.
Shot 3 (3.5-5.1s): Static macro 3D animation showing cross-section of an egg. Semi-transparent light blue arrows flow outward from the central yellow yolk representing osmotic dehydration, clean lighting.
```

**G5 · 镜头 #10 · 1.2s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 29.5–30.6s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D渲染，一只毛茸茸的可爱卡通小猴子站在画面左侧，看着右侧一个悬浮的毛茸茸白色圆球，背景是简单的浅绿色几何墙面和一个棕色罐子，柔和的影棚灯光，突出毛发质感，皮克斯风格，竖屏构图。
- 生成 4s 后剪到 1.2s（太短的镜头单独生成不稳定）
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。
3D动画，毛茸茸的可爱卡通小猴子站在左侧，看着右侧悬浮的毛茸茸白色圆球，小猴子有轻微的呼吸动作，白色圆球微微浮动，摄像机固定，柔和光线。
```

英文提示词：

```text
3D animation, a cute furry cartoon monkey standing on the left, looking at a floating furry white ball on the right. The monkey has slight breathing movements, the white ball floats slightly, fixed camera, soft lighting.
```

**G6 · 镜头 #11、#12 · 7.4s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 30.6–38.0s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D渲染，特写镜头，一个剖开的鸭蛋内部结构模型。中心是一个光滑的黄色球体代表蛋黄，外面包裹着半透明的白色蛋壳，底部放置在一个米色编织材质的环形底座上。浅绿色纯色背景，柔和的棚拍光线，卡通科普风格，干净明亮。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–3.1s）：3D动画，固定镜头。画面中心是一个剖开的鸭蛋结构模型，中心的黄色球体（蛋黄）随着时间推移逐渐按比例平滑缩小，其他部分保持静止。
镜头2（3.1–7.4s）：几个白色的毛茸茸小球生物原本分散趴在木质桌面上，随后它们向中间靠拢，紧紧挤在一起，接着从它们身上蹦出几个橙色的小圆球，镜头保持固定。
```

英文提示词：

```text
Shot 1 (0.0-3.1s): 3D animation, fixed camera. In the center of the frame is a cross-section model of a duck egg structure. The yellow sphere (egg yolk) in the center gradually and smoothly shrinks in scale over time, while the other parts remain stationary.
Shot 2 (3.1-7.4s): Several white fluffy little ball creatures are initially scattered on a wooden table. Then they move towards the center and huddle tightly together. Next, several small orange spheres pop out from them. The camera remains static.
```

**G7 · 镜头 #13 · 3.5s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 38.0–41.6s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D剖面渲染图，一颗剖开的熟咸鸭蛋模型，中央是圆润橙黄的蛋黄，外层是半透明凝胶状蛋白与外壳切片，极简柔和工作室灯光，居中构图，精致科普插画风格
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。
固定机位特写3D剖开的咸鸭蛋，橙黄色球形蛋黄顶部表面慢慢渗出亮晶晶的金黄色油脂并汇聚流动，蛋白与外壳静止，柔和的工作室顶光，平稳展示流体析出过程
```

英文提示词：

```text
Static close-up 3D animation of a cross-sectioned salted duck egg, golden oil droplets slowly oozing and gathering on top of the smooth orange yolk, soft studio overhead lighting, realistic fluid simulation, educational animation style.
```

**G8 · 镜头 #14–#16 · 8.0s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 41.6–49.6s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D极简科普渲染风格，灰色平滑背景与浅色台面，画面中央悬挂一块浅灰蓝色微绒毛方形毛巾，穿在一根横向金属细杆上，柔和均匀光照，干净的三维模型
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–3.7s）：固定平视机位，3D动画演示：中央带有细微毛绒的方形毛巾被左右两侧的金属杆向内推挤压缩成细长T字形，随着挤压，毛巾两侧空中生成数滴晶莹剔透的水滴向下坠落，背景保持极简静止
镜头2（3.7–5.8s）：3D卡通风格，三个毛茸茸的可爱小动物并排站立，中间绿色，两边棕色和灰色，背景是简单的绿色几何山丘和一个棕色罐子。画面上方有细小的黄色颗粒不断落下。固定镜头
镜头3（5.8–8.0s）：3D卡通风格，特写镜头，一个切开的咸鸭蛋模型放在白色容器中，蛋黄呈橙黄色。随着时间推移，蛋黄顶部逐渐溢出更多油脂，油脂表面有闪烁的星星特效，镜头保持固定。
```

英文提示词：

```text
Shot 1 (0.0-3.7s): Static eye-level shot, 3D educational animation: a light blue textured towel block suspended on a metal rod is squeezed inward from both sides by the rod mechanism, compressing into a tight T-shape, releasing transparent water droplets falling down on both sides, minimal studio background
Shot 2 (3.7-5.8s): 3D cartoon style, three fluffy cute little animals standing side by side, the middle one is green, the ones on the sides are brown and gray, the background is simple green geometric hills and a brown jar. Small yellow particles are continuously falling from the top of the screen. Static camera
Shot 3 (5.8-8.0s): 3D cartoon style, close-up shot, a cut salted duck egg model placed in a white container, the yolk is orange-yellow. Over time, more oil gradually overflows from the top of the yolk, with twinkling star effects on the oil surface, the camera remains fixed.
```

**G9 · 镜头 #17、#18 · 7.6s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 49.6–57.2s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D卡通风格，竖屏。左侧是一个毛茸茸的绿色小猴子角色，右侧是一个放在白色底座上的棕色小罐子，罐子顶部打开，露出黄色的蛋黄。背景是简单的浅绿色几何山丘形状。整体光线柔和均匀。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–5.4s）：3D动画。左侧的绿色毛绒角色保持静止。右侧原本是一个白色毛球，瞬间变成一个棕色小罐子。罐子顶部打开，一股粉红色的液体呈S型从上方蜿蜒流下，落在罐子里的黄色蛋黄上。固定镜头。
镜头2（5.4–7.6s）：3D动画，三只毛绒猴子，中间的猴子双手举起头顶的碗和咸鸭蛋，表情开心，旁边两只猴子轻微晃动，镜头固定。
```

英文提示词：

```text
Shot 1 (0.0-5.4s): 3D animation. A green fuzzy character on the left remains still. On the right, a white fuzzy ball instantly transforms into a small brown pot. The top of the pot opens, and a stream of pink liquid meanders down from above in an S-shape, landing on the yellow yolk inside the pot. Fixed camera.
Shot 2 (5.4-7.6s): 3D animation, three furry monkey characters, the middle monkey raises its hands holding a bowl and a salted duck egg on its head, happy expression, the two monkeys on the side sway slightly, fixed camera.
```

**G10 · 镜头 #19–#21 · 9.3s · 3D 渲染**

- 参考素材：`@图片1` 人物参考图（每个角色一张正脸 + 半身），保证跨镜头长相一致；`@视频1` 原片 57.2–66.5s 片段：参考动作、运镜和剪辑节奏（只作参考，不复制画面）
- 首帧图像提示词：3D渲染卡通毛茸茸小猴子玩偶，全身浓密逼真的绒毛，大眼睛微笑，黄色与棕色各一只，桌面摆放切开冒油的咸鸭蛋与褐色小坛子，极简干净背景，柔和演播室光照，竖屏构图。
- 另一条路：3D 工程。让 LLM 写 Blender 脚本或 Three.js 场景，角色/道具建模一次、按镜头设机位渲染，多角度和角色一致性最好，改文案和镜头也只是改代码（R08）

```text
竖屏 9:16；正面柔光（平光），柔光（几乎没有明暗分界），中性（约 5000K），背景明显虚化（浅景深/人像模式）。人物以 @图片1 为准。参考 @视频1 的动作、运镜和剪辑节奏。镜头之间硬切。
镜头1（0.0–3.5s）：固定镜头，两只毛茸茸的卡通小猴子站在桌前，棕色小猴子眨眼并微微抬手摆动，右侧滑入一个红色禁止标牌，角色毛发细腻无闪烁，整体画面平稳逼真。
镜头2（3.5–5.8s）：固定平视镜头，3D渲染木质天平。一个小蛋黄球从上方垂直掉落并融入左侧托盘的大蛋黄球中，天平横梁顺势向左下倾斜，随后上方弹出几个四角星光闪烁特效，最终天平保持倾斜静止。
镜头3（5.8–9.3s）：镜头固定，三个毛茸茸的卡通动物角色并排站立，角色轻微眨眼和晃动身体，背景中的几何圆球保持悬浮静止，光影保持稳定。
```

英文提示词：

```text
Shot 1 (0.0-3.5s): Static camera shot, two fluffy 3D cartoon monkeys standing in front of a table with salted duck eggs, the brown monkey blinks and moves slightly, a red prohibition sign enters from the right, realistic hair particle rendering, soft studio lighting.
Shot 2 (3.5-5.8s): Static eye-level shot, 3D rendered wooden scale. A small egg yolk ball falls from above and merges into a larger yolk ball on the left tray, causing the scale to tilt down to the left, followed by sparkling four-point star graphics popping up above, ending in a tilted rest.
Shot 3 (5.8-9.3s): Static camera, three fluffy cartoon animal characters standing side by side, characters slightly blinking and swaying their bodies, geometric spheres in the background remain suspended and still, stable lighting.
```
