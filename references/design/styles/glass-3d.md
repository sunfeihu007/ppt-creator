# 风格：玻璃拟态 3D（glass-3d）——颜色无关

> 来源方向：浅底玻璃材质、等距系统图与分层技术演示。只在用户明确需要玻璃材质时使用。
> 本文件不含任何具体品牌颜色，所有颜色以 `{TOKEN}` 引用所选配色文件。

## 风格概述

高端商务科技风。3D 玻璃质感卡片 + 立体分层架构 + 渐变图标徽章，信息承载力最强，
适合技术方案、平台架构、多 Agent 体系等复杂内容。**推荐搭配浅色配色**（深色配色不适用）。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in a restrained glass-morphism 3D family.
[COLOR_SCHEME]
Use an airy light field, a stable grid, translucent frosted surfaces, precise reflections,
soft depth and one coherent isometric or layered visual system. Preserve readable flat
labels and connectors on dense pages; not every module should become a floating 3D object.
Use consistent medium radius, thin highlights and one monochrome 3D icon family. Avoid
opaque metallic blocks, muddy dark areas, excessive glow, pill overload and dashboard slop.
```

> v2.5 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **背景**：`{BG}` 的轻微明度层级＋稀疏几何网格，不使用通用电路壁纸
- **玻璃卡片**：半透明白色圆角卡片，`{SECONDARY}` 描边高光，柔和投影，真实反射
- **3D 立体**：等距分层架构块（每层有厚度阴影），核心层用 `{PRIMARY}` 高亮发光
- **图标**：统一单色 3D 几何或真实对象，不使用通用脑、机器人、芯片徽章
- **数据流**：一条克制的 `{PRIMARY}` 细箭头或粒子路径
- **标签**：扁平、可读、贴近对象，不建立胶囊标签云
- **材质排他**：颜色必须以柔和渐变作用于透明/磨砂材质；禁止厚重不透明金属色和暗沉浑浊大色块

## 布局规范

- 信息密度：高（架构/对比页）到低（封面/过渡页）分级
- 常用骨架：中心辐射、等距分层塔、主系统＋窄注释栏、左右对分
- 同类卡片等宽等高水平对齐；标题区统一位置；避免头重脚轻

## 页面类型模板（旧版兼容）

> 使用时：脚本将所选配色文件的"提示词配色描述段"替换 `[COLOR_SCHEME]`，
> 参考图 `ref-*.jpg` 一并垫图，并声明"参考图仅参考布局与质感，配色以文字为准"。
> 所有模板必须遵守：Material Constraint — preserve translucency, frosted glass and
> airy gradients. NEVER use heavy fully opaque metallic colors or dark muddy blocks that
> break the glass illusion.

### 封面页
```
Create a premium professional PPT cover slide, 16:9, glass morphism 3D style.
[COLOR_SCHEME]
Title: [主题]（{TITLE}色大字，关键词用{PRIMARY}）; Subtitle: [副标题]
Elements: 一组3D玻璃质感分层立体块（平台意象）居右，漂浮图标徽章，细微网格纹理与光斑，
photorealistic reflections and soft shadows. Layout reference: attached image
(layout/texture only, IGNORE its colors).
```

### 架构/关系图页
```
Create a professional PPT architecture slide, 16:9, glass morphism 3D style.
[COLOR_SCHEME]
Content: [架构描述]
Elements: 3D等距分层架构或中心辐射节点图，玻璃透明层，{PRIMARY}数据流与高亮核心层，
统一单色系3D图标，每层文字标签完整显示。高信息密度但层次分明。
Layout reference: attached image (layout/texture only, IGNORE its colors).
```

### 内容页（主系统＋辅助面）
```
Create a professional PPT content slide, 16:9, glass morphism style.
[COLOR_SCHEME]
Title: [标题]; 一个主玻璃系统占主要面积，旁边用一大一小两个辅助面承载提供的要点。
保持不等宽层级、扁平文字标签和清晰连接；不生成三个等宽玻璃卡片或图标徽章墙。
Layout reference: attached image (layout/texture only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（架构）、ref-03（主系统＋辅助面）
