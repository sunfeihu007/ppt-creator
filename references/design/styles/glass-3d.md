# 风格：玻璃拟态 3D（glass-3d）——颜色无关

> 版式来源：联通知识管理平台 / 兴业银行审计智能体 / 明东码头（同一版式语言的红蓝两个实例）
> 本文件不含任何具体颜色，所有颜色以 `{TOKEN}` 引用所选配色文件。

## 风格概述

高端商务科技风。3D 玻璃质感卡片 + 立体分层架构 + 渐变图标徽章，信息承载力最强，
适合技术方案、平台架构、多 Agent 体系等复杂内容。**推荐搭配浅色配色**（深色配色不适用）。

## 视觉元素

- **背景**：`{BG}` 渐变 + 细微几何网格/电路纹理，边缘可有 `{PRIMARY}` 淡光晕
- **玻璃卡片**：半透明白色圆角卡片，`{SECONDARY}` 描边高光，柔和投影，真实反射
- **3D 立体**：等距分层架构块（每层有厚度阴影），核心层用 `{PRIMARY}` 高亮发光
- **图标**：`{SECONDARY}` 系渐变 3D 徽章质感，全局统一单色系，禁止彩色图标
- **数据流**：`{PRIMARY}` 发光粒子流、细箭头连接线
- **标签**：白底细描边小胶囊（协议名、机制名等短词）

## 布局规范

- 信息密度：高（架构/对比页）到低（封面/过渡页）分级
- 常用骨架：中心辐射（核心居中环绕）、三栏玻璃卡、等距分层塔、左右对分
- 同类卡片等宽等高水平对齐；标题区统一位置；避免头重脚轻

## 页面类型模板（生图提示词骨架）

> 使用时：脚本将所选配色文件的"提示词配色描述段"替换 `[COLOR_SCHEME]`，
> 参考图 `ref-*.jpg` 一并垫图，并声明"参考图仅参考布局与质感，配色以文字为准"。

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

### 内容页（三栏卡片）
```
Create a professional PPT content slide, 16:9, glass morphism style.
[COLOR_SCHEME]
Title: [标题]; 三个并排玻璃圆角卡片，每卡=3D图标徽章+{PRIMARY}小标题+3行{BODY}说明。
等宽等高对齐，留白适当。
Layout reference: attached image (layout/texture only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（架构）、ref-03（三栏卡片）
