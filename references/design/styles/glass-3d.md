# 风格：玻璃拟态 3D（glass-3d）——颜色无关

> 来源方向：浅底玻璃材质、等距系统图与 Apple HIG 的材质层级原则。只在用户明确需要
> 玻璃材质时使用；吸收层级与可读性方法，不复制 Apple 界面、控件或品牌资产。
> 本文件不含任何具体品牌颜色，所有颜色以 `{TOKEN}` 引用所选配色文件。

## 风格概述

高端、明亮、产品化的专项科技风。以稳定实色内容层承载文字和结构，只让一个磨砂玻璃焦点层
表达前后层级；适合产品封面、平台总览、核心能力和低到中密度系统图。高密架构、流程、表格
和对比页必须降低透明度并平面化节点。**推荐搭配浅色配色**（深色配色不适用）。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in a restrained glass-morphism 3D family.
[COLOR_SCHEME]
Use an airy light field, a stable grid, a solid content layer, and at most one restrained
frosted focal layer with precise reflections and soft depth. Use no more than two translucent
layers in total and never place light glass on light glass. Preserve readable flat labels,
tables, connectors and opaque or near-opaque nodes on dense architecture, flow and comparison
pages; not every module should become a floating 3D object.
Use consistent medium radius, thin highlights and one monochrome 3D icon family. Avoid
opaque metallic blocks, muddy dark areas, excessive glow, pill overload and dashboard slop.
```

> v2.6 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **背景**：`{BG}` 的轻微明度层级＋稀疏几何网格，不使用通用电路壁纸
- **内容层**：文字、表格、架构节点使用 `{SURFACE}` 实色或高不透明表面，首先保证可读
- **玻璃焦点层**：最多一个主要磨砂层和一个辅助透明层；禁止浅玻璃叠浅玻璃
- **3D 立体**：一组等距分层系统；只让核心层使用 `{FOCUS}` 建立聚焦，不让全部对象悬浮
- **图标**：统一单色 3D 几何或真实对象，不使用通用脑、机器人、芯片徽章
- **数据流**：一条克制的 `{PRIMARY}` 细箭头或粒子路径
- **标签**：扁平、可读、贴近对象；玻璃上的文字必须有实色承载或足够不透明的背板
- **材质排他**：颜色必须以柔和渐变作用于透明/磨砂材质；禁止厚重不透明金属色和暗沉浑浊大色块

## 材质层级

1. 背景层保持低噪声，不用全屏玻璃壁纸。
2. 内容层保持实色或高不透明，负责文字、表格、架构与证据。
3. 焦点层使用一次玻璃材质，负责核心系统或单一重点。
4. 总透明层级最多两层，禁止玻璃叠玻璃。
5. `architecture / flow / compare-kpi` 页面自动平面化普通节点，只保留一个玻璃焦点。

## 布局规范

- 信息密度：低到中为主；架构/对比页可到中高，但必须平面化普通节点
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
