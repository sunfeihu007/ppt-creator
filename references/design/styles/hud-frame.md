# 风格：HUD 线框（hud-frame）——仅限深色配色

> 来源方向：深色工程监测、线框场景和技术概念演示。⚠️ 只能搭配 `deep-space`，
> 且须用户明确接受深色背景。适合创新立项、概念演示和评奖路演。

## 风格提示词骨架

```
Create a professional 16:9 presentation slide in a dark technical HUD-line family.
[COLOR_SCHEME]
Use a disciplined dark grid, thin luminous frames, orthogonal connectors, restrained
scanning brackets, mono technical labels and one coherent wireframe object language.
Keep small text high-contrast and readable. Reserve glow for the primary focal system;
large dark quiet areas provide breathing room. Avoid multicolor cyberpunk, fictional
metrics, dense decorative telemetry, game-interface chrome and unrelated sci-fi scenery.
```

> v2.6 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **HUD线框**：{PRIMARY}细发光描边框、四角括号取景框、扫描线
- **3D线框实体**：主题实体（集装箱/建筑/设备）用{PRIMARY}发光线框+半透明面构建
- **数据标注**：只显示用户提供且有来源的参数；没有数据时使用结构名称，不虚构精度或时延
- **辉光**：主元素外发光；{PRIMARY}粒子、光束、景深
- **警示**：关键风险用{WARN}高亮
- **术语**：中文为主，仅为用户提供的正式英文术语保留原文

## 布局规范

- 中高密度；深色下留白靠"暗区"实现
- 主视觉居中/居右，参数标注环绕；路线图=横向发光轴+节点光柱
- 小字与背景对比度必须足够（{TITLE}近白）

## 页面类型模板（旧版兼容）

### 封面页
```
Create a sci-fi HUD style PPT cover slide, 16:9. [COLOR_SCHEME]
标题：[主题]（{TITLE}粗体大字）+{BODY}细体副标题。
右侧3D发光线框场景（[主题实体]），HUD取景框与扫描元素；只有来源明确时才显示参数标签，
{PRIMARY}粒子与光束。所有文字清晰可读。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

### 目录页
```
Create a sci-fi HUD style PPT contents slide, 16:9. [COLOR_SCHEME]
标题左对齐。沿一条水平扫描轴排列真实目录条目，当前条目用一个发光框聚焦；
其余条目使用直接标签和细线连接，不建立多行圆角卡片墙。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

### 内容页
```
Create a sci-fi HUD style PPT slide, 16:9. [COLOR_SCHEME]
标题：[标题]（{TITLE}粗体）。主视觉发光线框示意图（[描述]），
HUD标注框只列用户提供的要点；只有真实风险语义才使用{WARN}，普通重点使用{PRIMARY}。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

参考图：ref-01（封面）、ref-02（目录）、ref-03（内容）
