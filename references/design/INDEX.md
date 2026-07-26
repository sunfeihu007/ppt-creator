# PPT Creator 视觉系统索引（v5 / Skill v2.6）

> 核心公式：**整套风格家族 × 单页页面类型 × 整套行业视觉修饰 × 语义配色**。
> 内容规划仍由 Phase 1–3 完成；本目录只决定内容如何被视觉化。

## 一、四层视觉系统

| 层 | 控制范围 | 是否整套锁定 | 作用 |
|:---|:---|:---:|:---|
| 风格家族 `style` | 整套 PPT | 是 | 字体层级、网格、材质、圆角、线条、阴影、图片和图标语言 |
| 页面类型 `page_type` | 单页 | 否 | 封面、架构、流程、案例等页面各自的构图语法 |
| 行业视觉修饰 `industry` | 整套 PPT | 是 | 行业相关几何、图像、图标和视觉语气；不添加行业内容 |
| 语义配色 `palette` | 整套 PPT | 是 | 背景、结构、聚焦、文字、边界与状态色的角色分工 |

一套 PPT 必须锁定同一 `palette × style × industry × provider`。页面只通过 `page_type`
和 `layout_hint` 产生节奏变化，不能临时换风格、换材质或换色。

## 二、选择优先级与分级

1. **客户品牌优先**：真实 VI、Logo、字体和模板高于本系统默认值。
2. **公司品牌其次**：没有客户品牌限制时，公司方案默认 `orange-teal`。
3. **行业方案作视觉兜底**：行业建议不改内容，也不覆盖客户品牌。
4. **优先 Core**：新项目先从 Core 配色和风格中选。
5. **兼容矩阵把关**：`blocked` 必须拒绝；`specialized/legacy` 必须说明原因。

### 组合状态

| 状态 | 含义 |
|:---|:---|
| `recommended` | 首选组合；每套配色最多 3 个 |
| `allowed` | 兼容，但不是默认 |
| `specialized` | 只有明确材质意图时使用 |
| `legacy` | 兼容既有项目；新项目给出现代替代 |
| `blocked` | 材质、主题或语义直接冲突，必须拒绝 |

机器事实分工：

- `compatibility.json`：13 × 9 的完整交叉组合；
- `governance.json`：单个风格/配色的层级、密度、几何、圆角、阴影、字体、空间锚点、
  素材和参考图策略；
- `reference-manifest.json`：中性参考图的角色、尺寸与 SHA-256。

## 三、可用配色（13 套）

| 配色 ID | 层级 | 结构色 / 聚焦色 | 适合方向 |
|:---|:---|:---|:---|
| `orange-teal` | Core | 深青绿 / 橙 | 公司默认、港口、综合解决方案 |
| `finance-navy-teal` | Core | 藏青 / 深青绿 | 银行、保险、审计、金融科技 |
| `industrial-navy-orange` | Core | 工业藏青 / 安全橙 | 汽车、制造、工业 AI |
| `ink-paper` | Core | 深墨 / 藏青 | 正式咨询、案例、研究、高层汇报 |
| `swiss-ikb` | Core | 近黑 / IKB 蓝 | 科技发布、数据演讲、对外交流 |
| `graphite-cobalt` | Core | 石墨 / 钴蓝 | 克制通用科技、AI、产品与方案 |
| `porcelain-azure` | Conditional | 石墨 / 晴蓝 | 明亮产品、AI、金融科技与高端客户方案 |
| `liantong-red` | Brand | 深灰 / 品牌红 | 仅在对应品牌体系中使用 |
| `navy-gold` | Conditional | 藏青 / 金 | 正式高层、典礼型低频重点 |
| `forest-ivory` | Conditional | 森林绿 / 陶土 | 绿色港口、低碳制造、ESG 专项 |
| `deep-space` | Specialized | 深藏青 / 荧光青 | 只服务深色 HUD |
| `tech-blue` | Legacy | 深蓝 / 科技蓝 | 旧浅蓝渐变科技稿兼容 |
| `warm-orange` | Legacy | 暖深色 / 橙 | 旧暖调叙事稿兼容 |

`graphite-cobalt` 是新项目中替代通用浅蓝渐变“科技模板”的冷静选择；`porcelain-azure`
提供更温润、明亮、产品化的 Conditional 方向。公司品牌汇报仍优先 `orange-teal`，行业方案
仍优先相应行业色板。

### 16 个语义 Token

每个 palette 必须定义：

- 背景/表面：`{BACKGROUND}`、`{SURFACE}`；
- 结构/聚焦：`{STRUCTURE}`、`{FOCUS}`；
- 浅底文字：`{FOCUS_TEXT}`、`{TEXT_PRIMARY}`、`{TEXT_SECONDARY}`；
- 边界/反相：`{BORDER}`、`{INVERSE_BACKGROUND}`、`{INVERSE_TEXT}`；
- 状态填充/线：`{STATUS_OK}`、`{STATUS_WARN}`、`{STATUS_RISK}`；
- 状态文字：`{STATUS_OK_TEXT}`、`{STATUS_WARN_TEXT}`、`{STATUS_RISK_TEXT}`。

`FOCUS` 和 `STATUS_*` 是色块、线条和图标颜色，不能直接当普通小字色。小字使用对应
`*_TEXT`，验证器会检查它们在 `{BACKGROUND}` 和 `{SURFACE}` 上至少达到 4.5:1。
旧 `{PRIMARY}`、`{SECONDARY}`、`{ACCENT}`、`{BG}` 等 Token 继续兼容旧模板。

### 配色纪律

- 品牌强调色和状态色是两套体系；风险红不作普通重点，品牌橙不替代警告。
- 每页只有一个主要聚焦对象；图表其余系列灰化或同色阶处理。
- `orange-teal` 遵守约 85-12-3；`industrial-navy-orange` 安全橙通常不超过 5%。
- `forest-ivory` 陶土色通常不超过 5%；`deep-space` 不因主题是“AI”就自动使用。
- 平面风格会把 palette 中的背景渐变解释为同色系明度层级，不绘制可见渐变。

## 四、可用风格（9 种）

| 风格 ID | 层级 | 核心视觉语法 | 密度 | 参考 |
|:---|:---|:---|:---:|:---:|
| `swiss-grid` | Core | 12 栏、直角、发丝线、单一锚点色 | 中 | 文字骨架 |
| `industrial-diagram` | Core | 工程网格、正交连接、设备线描 | 中高 | 文字骨架 |
| `flat-editorial` | Core | 大字号、编辑留白、平面色块 | 低中 | 3 张 |
| `product-evidence` | Core | 主证据面、窄注释栏、来源带 | 中 | 3 张 |
| `lineart-minimal` | Conditional | 单色细线、一个主线描、大留白 | 低 | 3 张 |
| `card-modern` | Conditional | 折角模块、超大数字、非对称模块 | 中 | 3 张 |
| `illust-2.5d` | Conditional | 等距插画、旅程路径、亲和叙事 | 中低 | 3 张 |
| `glass-3d` | Specialized | 实色内容层、单一玻璃焦点、克制反射 | 低中到中高 | 3 张 |
| `hud-frame` | Specialized | 深底线框、正交连接、真实参数 | 中高 | 3 张 |

### `product-evidence` 的职责

- 一张真实截图、照片、图解或明确标注的方案示意占 55–70%；
- 一个窄注释栏只陈述用户提供的事实；
- 项目契约要求时显示来源/真实性标签；
- 禁止假 UI、假客户 Logo、假指标、装饰设备样机和三台手机并排。

### 整套视觉锁

`governance.json` 为每个 style 固定：

- 密度与版式变化范围；
- 几何、圆角和阴影系统；
- 材质优先级；
- 字体家族预算、3–5 级层次、大标题/正文/小字规则；
- 标题轴、语义对象和章节转换的跨页空间锚点；
- 图片与注释规则；
- 单页微标签预算；
- 参考图模式。

这些规则由 `make_prompt.py` 自动注入，不增加用户确认点。

`glass-3d` 额外限定最多两级透明材质、禁止玻璃叠玻璃，并要求
`architecture / flow / compare-kpi` 页面平面化普通节点，只保留一个玻璃焦点。

## 五、页面类型（11 类）

| 页面类型 | 视觉职责 | 关键规则 |
|:---|:---|:---|
| `cover` | 封面 | 一个主视觉，不做卡片墙 |
| `toc` | 目录 | 稳定编号与网格，不为每项配装饰图标 |
| `section` | 章节 | 低密度停顿，可同色板反白 |
| `overview` | 总览 | 一个关系系统或少量统一模块 |
| `architecture` | 架构 | 模块对齐、连接明确、只高亮一个核心层 |
| `flow` | 流程/数据流 | 单一阅读方向、统一节点与箭头 |
| `detail` | 详解 | 非对称图文或主模块＋窄注释栏 |
| `compare-kpi` | 对比/数据 | 对比逻辑明确、关键值聚焦、不造数据 |
| `case` | 客户案例 | 真实图片/截图优先，不编客户 Logo |
| `roadmap` | 实施计划 | 一条阶段主轴或阶段门 |
| `closing` | 总结/结束 | 呼应封面，低密度，不虚构联系方式 |

旧 `template` 会自动映射到上述类型，不改变原有内容字段。

## 六、行业视觉修饰（4 类）

| 行业 ID | 视觉关键词 | 默认建议 |
|:---|:---|:---|
| `general` | 中性商务、内容驱动、克制几何 | `orange-teal × swiss-grid` |
| `port-terminal` | 堆场网格、泊位/路径、设备线描 | `orange-teal × industrial-diagram` |
| `finance` | 制度化网格、发丝线、精确表格 | `finance-navy-teal × flat-editorial` |
| `automotive-manufacturing` | 装配网格、正交系统线、设备轮廓 | `industrial-navy-orange × industrial-diagram` |

行业修饰器只影响画面语言：

- 港口不等于赛博蓝；优先宽幅、空间关系和工程节奏。
- 金融不等于金色；优先可信、精确、证据和低材质噪声。
- 汽车制造不靠金属渐变；工业感来自结构、比例和真实素材。
- ESG 是专项方向，不让所有港口或制造汇报自动变绿。

## 七、常用推荐

| 场景 | 首选 |
|:---|:---|
| 公司通用技术/AI 方案 | `orange-teal × swiss-grid × general` |
| 中性技术/产品介绍 | `graphite-cobalt × product-evidence × general` |
| 明亮产品/AI/金融科技介绍 | `porcelain-azure × product-evidence × general` |
| 港口码头方案 | `orange-teal × industrial-diagram × port-terminal` |
| 港口产品/案例页为主 | `orange-teal × product-evidence × port-terminal` |
| 金融方案 | `finance-navy-teal × flat-editorial × finance` |
| 金融架构密集 | `finance-navy-teal × swiss-grid × finance` |
| 汽车/制造方案 | `industrial-navy-orange × industrial-diagram × automotive-manufacturing` |
| 正式案例/研究 | `ink-paper × product-evidence × general` |
| 科技发布/大字演讲 | `swiss-ikb × swiss-grid × general` |
| 绿色港口/低碳制造专项 | `forest-ivory × flat-editorial × 对应行业` |

## 八、整套节奏预检

Phase 4 和 Phase 7 运行：

```bash
python scripts/verify_design_plan.py
```

它会：

- 阻止未登记或 blocked 组合；
- 对 specialized/legacy 选择给出说明；
- 发现连续 3 页同一布局族；
- 发现三等分卡片/卡片墙跨页重复。

默认只让错误阻塞；`--strict` 可把警告也作为失败。页面类型相同不等于版式相同，检测主要依据
`layout_hint`，因此 Phase 3 应写清楚视觉布局提示。

## 九、参考图规则

- 7 个带参考图的风格共有 21 张 1600×900 JPEG。
- 参考图由 `scripts/generate_style_refs.py` 生成，保证无文字、无品牌、无数据、配色中性、无 EXIF。
- `reference-manifest.json` 保存角色、尺寸和 SHA-256；`validate_design.py` 会校验。
- 参考图只携带版式和材质信息，不能复制其中的文字、Logo、日期、版本、指标或客户事实。
- `swiss-grid` 和 `industrial-diagram` 使用完整文字骨架，不虚构参考图参数。
- AGY 原生当前没有独立参考图参数，继续依靠完整提示词、样张和 QA。

重建与检查：

```bash
python scripts/generate_style_refs.py
python scripts/generate_style_refs.py --check
```

## 十、参考来源与转化边界

本版吸收方法，不复制其他 Skill 的代码、内容流程或交付格式：

| 参考来源 | 吸收的方法 | 在 PPT Creator 中的落点 |
|:---|:---|:---|
| Taste Skill | 先审计再改、反默认三卡、一个强调色、形状一致、版式不连续重复、真实截图优先、假精确数字禁令 | 治理 profile、节奏预检、参考资产重建、`product-evidence` |
| 花叔 Design | 品牌资产优先、反 AI slop、系统优先、真实素材优先、代表性样张 | 品牌优先级、案例真实资产规则、合并样张 |
| 归藏 PPT Skill | 瑞士网格、单一锚点色、直角纯色、墨纸/森林纸面方向 | `swiss-grid`、`swiss-ikb`、`ink-paper`、`forest-ivory` |
| PPT Master | 身份/结构分层、页面类型索引、规格锁定、逐页按同一 spec 执行 | 四层模型、`page_type`、整套视觉锁、机器校验 |
| Apple Design Skill / Apple HIG | 材质承担层级而非装饰、玻璃不铺满内容层、字体按字号调整字距与行距、空间锚点一致 | `glass-3d` 两级透明上限、九种 style 字体治理、跨页空间一致性、`porcelain-azure` |

Apple 参考：
[Apple Design Skill](https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md)、
[Materials](https://developer.apple.com/design/human-interface-guidelines/materials)、
[Typography](https://developer.apple.com/design/human-interface-guidelines/typography)、
[Color](https://developer.apple.com/design/human-interface-guidelines/color)。

没有引入 Taste 或 Apple Design 的手势、弹簧、动效、响应式、导航、CTA、表单和 Web 技术栈
规则；没有复制 Apple 动态系统色、界面控件或品牌资产；没有引入花叔的 HTML 交付、归藏的
固定 HTML 模板或 PPT Master 的 SVG 流水线。PPT Creator 继续使用七阶段、整页图片生成和
PPTX 组装方式。

## 十一、截图、网站与 PPT 视觉参考

用户带来截图或网址时，先读 `visual-reference-intake.md`，并运行：

```bash
python scripts/intake_visual_reference.py --help
```

一张截图只建立 palette 或单页 layout 候选；完整 style 至少需要 4 张参考图和 4 种
`page_type`。脚本不复制源图、不修改正式注册表，并固定要求完成来源、查重、16 个语义 Token、
跨行业通用性、三页中性样张和用户批准后才能晋级。

Palette 三页样张：

```bash
python scripts/generate_palette_preview.py \
  --palette porcelain-azure --output /path/to/preview
```

## 十二、扩展与校验

新增或删除资源后必须：

1. 为 palette × style 的全部组合登记状态；
2. `blocked/legacy` 写原因和替代，`specialized` 写使用理由；
3. 每套 palette 补齐 16 个语义 Token 和旧兼容 Token；
4. 每个 style 补齐治理 profile、字体字段与风格骨架；
5. 带参考图的 style 登记 3 个角色并更新 manifest；
6. 运行：

```bash
python scripts/validate_design.py
python scripts/verify_design_plan.py --plan /path/to/plan.json
```

验证器拒绝未登记组合、缺失 Token、文字对比度不足、治理字段缺失、参考图损坏/漂移、
无效索引和被禁止的行业默认组合。
