# 风格：产品证据（product-evidence）——颜色无关

> 来源方向：产品发布演示、客户案例板、现场照片注释和真实界面讲解。适合产品介绍、
> 客户案例、售前演示和方案证据页。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in a product-evidence family.
[COLOR_SCHEME]
Let one source-backed screenshot, photograph, diagram, or explicitly labeled conceptual
scene occupy 55-70% of the canvas. Pair it with one narrow annotation rail and, when the
project contract requires it, a compact provenance band. Use a stable grid, square or
small-radius evidence frames, direct factual callouts, restrained hairlines and one focal
color. Preserve the real asset without inventing UI, logos, metrics, dates, version labels,
device chrome or customer facts. Do not use a three-equal-card grid, fake dashboard,
decorative phone mockup, generic AI brain, robot, chip or shield.
```

## 视觉语法

- **主证据面**：真实截图、照片、架构图或已明确标注的方案示意，占画面 55–70%。
- **注释栏**：窄栏列出用户提供的事实；引导线不穿过正文。
- **来源带**：需要时展示 `provenance_label` 或来源说明，不装饰版本号和日期。
- **几何**：直角或统一小圆角；一个主框，不套多层设备外壳。
- **颜色**：结构色组织页面，聚焦色只标一个证据点。
- **禁止**：假 UI、假客户 Logo、假指标、假时间戳、三台手机并排和装饰性截图框。

## 页面类型模板（旧版 make_prompt.py 兼容）

### 产品介绍页

```
Create a product-evidence PPT slide, 16:9. [COLOR_SCHEME]
主截图或产品实物图占左侧约三分之二，右侧窄注释栏只使用提供的标题和要点；
一处聚焦标记连接真实画面细节。无假界面、无设备样机外壳、无虚构版本信息。
```

### 客户案例页

```
Create a customer-case evidence slide, 16:9. [COLOR_SCHEME]
一张真实现场/产品图或明确标注的方案示意作为主视觉，配一条事实栏和必要来源带；
不得生成客户Logo、客户名称、数字效果或未提供的现场细节。
```

### 证明/对比页

```
Create an evidence comparison slide, 16:9. [COLOR_SCHEME]
使用一个主证据面加前后状态或局部放大注释，保持同一图像处理方式和单一聚焦色；
不使用三等分卡片、评分条或虚构精确数字。
```

## 使用边界

- 没有真实素材时可以使用 AI 方案示意，但必须服从项目契约中的可见来源标签。
- 不能用画出来的假产品界面替代真实截图，也不能把通用素材包装成客户现场。
- 证据不足时减少视觉断言，不通过装饰补齐“可信感”。
