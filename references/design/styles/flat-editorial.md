# 风格：平面杂志排版（flat-editorial）——颜色无关

> 来源方向：咨询报告、机构杂志与证据型方案演示。
> 无3D无光效，靠字号对比、细线、真实素材与留白建立高级感。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in a flat editorial-consulting family.
[COLOR_SCHEME]
Use a strict baseline grid, decisive typography, asymmetrical editorial composition,
hairline rules, disciplined image crops and generous negative space. Prefer one clear
visual argument over a matrix of identical cards. Use no 3D, no glow, no glass, no
decorative gradient, and almost no shadow. Keep titles, headers, footers, image captions
and diagram labels consistent across every page type.
```

> v2.5 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **平面色块**：一处结构色平面与一处真实图像/图解建立张力，不套卡片头条
- **大数字序号**：只表达真实目录或数据，不添加装饰性编号
- **细节点缀**：`{SECONDARY}` 只做标题短线、分隔线或一个章节标记
- **文字层级**：以中文内容为主；只有用户提供的正式术语才附英文
- **页眉页脚**：统一标题轴和页码；不添加版本、日期或微型装饰文案
- **图标极少**：以排版为主，仅单色细线图标

## 布局规范

- 低中密度，留白是设计的一部分；严格网格对齐
- 骨架：目录左右对分；内容页主论点＋窄证据栏；场景页一张主图＋直接注释
- 信息三级：{SECONDARY}小标 → {PRIMARY}大标 → {BODY}说明

## 页面类型模板（旧版兼容）

### 封面页
```
Create a premium PPT cover slide, 16:9, flat editorial/magazine layout, NO 3D, NO glow.
[COLOR_SCHEME]
左侧60%为{PRIMARY}平面或斜切结构：{SECONDARY}短竖线+白色特大标题[主题]+白色细体副标题；
右侧40%留白或使用一个来源明确的主题图像。不得补日期、单位或版本信息。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 目录页
```
Create a PPT contents slide, 16:9, flat editorial layout. [COLOR_SCHEME]
左侧：{PRIMARY}特大标题"汇报大纲"+一句{BODY}说明。
右侧：[N]个真实条目纵向排列：{PRIMARY}序号+条目名（{PRIMARY}粗体）+
细灰分隔线。全部左对齐，不添加英文装饰小标。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 内容页（主论点＋证据栏）
```
Create a PPT content slide, 16:9, flat editorial layout. [COLOR_SCHEME]
标题：[标题]（{PRIMARY}粗体+{SECONDARY}短竖线）。使用一个占主要面积的论点、图解或真实素材，
配一个窄证据/说明栏和一条细灰基线；按内容层级排版，不生成等宽卡片矩阵或英文微标签。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（目录）、ref-03（主论点＋证据栏）
