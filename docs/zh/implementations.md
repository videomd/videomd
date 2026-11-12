# 实现

> 本文是 [implementations.md](../implementations.md) 的中文版。

生成或读取 VIDEO.md 拆片包的工具。想加上你的工具，提一个 pull request，在对应的表格里加一行；生成拆片包的工具，输出应当能通过 `videomd check`。

## 生成方（写拆片包）

| 工具 | 说明 |
|---|---|
| [rea-video](https://github.com/JuneYaooo/rea-video) | 逐镜拆解：每镜的制作方式、真实素材、声音、包装、复刻方案。每次拆解都会写出拆片包，包含制作方式判断、帧图、分轨音频和完整数据。 |

## 读取方（读拆片包）

| 工具 | 说明 |
|---|---|
| [videomd](https://github.com/videomd/videomd/tree/main/src/videomd/)（本仓库） | 参考读取库和校验器：`videomd check`、`videomd read`。 |
