# PPT Creator —— 结构化演示文稿生成 Skill

> 当前版本 v2.5.0 · MIT License

一个面向 AI Agent 的 PPT 制作技能：与你对话式地规划大纲和内容，按升级后的
“风格 × 页面类型 × 行业视觉 × 语义配色”四层系统，用 AI 并行生成、逐页质检高质量幻灯片图片，
通过项目事实契约锁定术语、声明边界和来源，在多轮修改后自动失效旧页面，最终组装成带演讲者
备注、自动大纲和交付清单的 PPTX 文件。

兼容所有支持 Agent Skills（SKILL.md）标准的 agent：**AGY CLI、Codex CLI / Codex 桌面端、
Claude Code / Cowork、Hermes Agent、OpenClaw** 等。

---

## 它能做什么

- **对话式规划**：不是拿到一句话就开画，而是先和你讨论清楚——给谁看、讲多久、分几个
  部分、每页讲什么，确认后才动手；
- **四层设计系统**：12 套语义配色 × 9 种风格（108 个显式校验组合）＋11 类页面构图＋
  4 个行业视觉修饰器；支持客户品牌、公司品牌和行业兜底的明确优先级；
- **并行 AI 生图**：多页任务默认至少4个子 agent 并行生成 16:9 高清整图，玻璃拟态 3D、杂志排版、
  极简线描、科幻 HUD 等质感均可；
- **演讲者备注**：每页自动写入带时长标注的演讲备注（重点页 5-6 分钟/过渡页 1-2 分钟，
  含互动与转折提示）；
- **工程化流程**：七步流程状态化管理，中断可恢复、换 agent 可接续；产物自动校验、
  自动压缩，成品直接可分发。
- **低干预确认**：图片阶段默认只确认设计样张和全套总览；有返工时最多增加一次，总计不超过3次。
- **事实与同步保障**：客户方案可记录必需词、禁止词、能力边界、来源和素材真实性；修改后只重做
  受影响页面，最终组装前拒绝使用过期产物。

## 当前版本亮点

- **状态化七步流程**：`plan.json` 记录阶段、页面和设计状态，任务中断后可继续；
- **四层视觉组合**：整套风格 × 单页页面类型 × 整套行业修饰 × 整套语义配色；
- **12 × 9 兼容矩阵**：108 个基础组合全部显式登记，推荐、可用、专项、旧版和冲突状态分开；
- **整套视觉治理**：风格自动锁定密度、几何、圆角、阴影、材质、素材和微标签预算；
- **文字对比度校验**：聚焦/状态填充色与可读文字色分离，文本角色自动检查 4.5:1；
- **版式节奏预检**：生成前发现连续同构页面和跨页重复三等分卡片/卡片墙；
- **中性参考资产**：21 张参考图全部无文字、无品牌、无假数据，并用清单和哈希校验；
- **行业只修饰视觉**：港口、金融、汽车制造只改变图形、素材和视觉语气，不介入内容规划；
- **旧计划无痛迁移**：旧 template 自动映射标准页面类型，旧计划默认使用通用行业修饰；
- **宿主原生生图**：AGY 默认调用原生 Gemini Nano Banana 2，Codex 默认调用原生 ImageGen；
- **其他客户端直连 Gemini**：使用 API key 调用稳定版 `gemini-3.1-flash-image`；
- **整套模型锁定**：provider、transport、model 写入计划，禁止中途静默换模型或混用；
- **显式兼容桥**：保留 AGY CLI 与 Codex CLI 桥接，但不参与默认路由；
- **交付质量保障**：生成前有全局约束，生成后经过机器校验、人工目检和组装 gate。
- **三档事实保障**：`standard / client-facing / evidence-sensitive` 按使用场景调整校验强度；
- **变更自动传播**：页面、契约、来源、设计或生图后端变化时，基于内容哈希精确失效旧产物；
- **语义级 QA**：生图前精确检查术语和声明，生图后可接入 OCR 文本复核；
- **精确页面复用**：导航页等完全相同的画面只生成一次，复用页保留独立演讲备注；
- **最终同步交付**：自动导出 `final_outline.md` 和 `artifact_manifest.json`。

## 适用场景

企业技术方案、产品介绍、立项汇报、培训课件、学术报告、销售交流。
对话中说"做个 PPT / 帮我做个汇报 / 生成演示文稿"即可触发。

---

## 七步工作流

| Phase | 做什么 | 产出 |
|:--|:--|:--|
| 1 大纲讨论 | 场景/受众/时长/保障级别 → 3-5 个主要部分 | 大纲框架 |
| 2 内容方向 | 核心要点＋关键术语/声明/来源 | 内容规划与项目契约 |
| 3 页数分配 | 逐页清单、页面引用和精确复用关系 | `plan.json` |
| 4 设计确定 | 品牌优先级 → 配色 → 风格 → 行业视觉修饰 → 生图后端 | 完整视觉锁定 |
| 5 框架页 | 样张确认后并行生成；AI逐页质检 | 框架页图片 |
| 6 内容页 | 至少4路并行生成 + AI目检 + 可选OCR语义核验 | 全部页面图片 |
| 7 整合输出 | 页面/语义/同步 gate → 组装 → 备注/大纲/清单 | 最终交付包 |

**防跳步与防漂移机制**：进度、当前需求决策、来源引用和产物哈希写入
`ppt_workspace/plan.json`。页面用 `qa_passed` 区分 AI 质检与用户批准；`build_ppt.py`
拒绝组装未确认、语义违规或输入已经变化的旧页面。

**合并返工语义**：全套总览中若只点名少数页面修改，其他已通过AI质检的页面立即视为批准，
只有点名页面退回重做；返工结果统一放在第3次、也是最后一次图片确认中。

---

## v2.5 视觉治理

v2.5 不改变七阶段和 v2.4 项目契约，而是把“风格和配色建议”变成可执行规则：

- 配色分为 Core、Brand、Conditional、Specialized、Legacy；
- 风格分为 Core、Conditional、Specialized；
- `recommended / allowed / specialized / legacy / blocked` 五种组合状态各有明确语义；
- 每套配色最多推荐 3 种风格，避免“几乎什么都推荐”；
- 平面风格自动压平 palette 的渐变语义，玻璃/HUD 与冲突色板直接阻止；
- `verify_design_plan.py` 在样张前和组装前检查整套版式节奏；
- `make_prompt.py` 自动注入形状、圆角、阴影、材质、素材与微标签锁。

本版新增：

- `graphite-cobalt`：冷灰＋石墨＋单一钴蓝，作为新项目的克制通用科技色；
- `product-evidence`：真实截图/照片/图解主导，配窄注释栏和必要来源带；
- 4 个可读文字角色：`FOCUS_TEXT / STATUS_OK_TEXT / STATUS_WARN_TEXT /
  STATUS_RISK_TEXT`；
- 21 张可复现的中性参考图，替换含客户、Logo、日期、版本、假指标或通用 AI 装饰的旧参考。

公司品牌汇报仍以 `orange-teal` 为默认；`graphite-cobalt` 不是覆盖公司色，而是替代旧式
浅蓝渐变通用科技模板。`tech-blue` 和 `warm-orange` 继续支持旧稿，但不再推荐给新项目。

---

## v2.4 项目事实契约

三种保障级别不会改变大纲，只改变事实校验强度：

| 等级 | 适用场景 | 行为 |
|:--|:--|:--|
| `standard` | 普通内部汇报、培训、创意内容 | 契约可选；兼容最轻 |
| `client-facing` | 客户方案、售前、产品介绍 | 检查术语与声明；案例证据缺失时警告 |
| `evidence-sensitive` | 真实案例、金融、合规、招投标 | 实证必须有来源；概念案例必须标“方案示意”等标签 |

契约支持：

- `requirements`：正式名称、必需词、禁止词和用户决策；
- `claim_constraints`：能力边界、责任、审批、数字和禁止承诺；
- `source_registry + source_refs`：页面依据的文件、用户确认或真实素材；
- `evidence_level + provenance_label`：区分真实、匿名、通用和 AI 方案示意；
- `reused_from + exact_asset`：完全相同页面直接复用同一图片；
- `prompt_input_hash / image_input_hash`：内容变化后自动识别过期产物。

当前交付模式固定为 `raster_slide`：每页是整张图片，演讲备注可编辑，但页面文字和图形不是
PowerPoint 原生对象。自 v2.4 起会明确披露这一点，不会把图片式 PPT 描述成原生可编辑。

完整规则见 `references/project-contract.md`。

---

## 四层视觉系统

v2.3 把“选一套颜色＋选一种质感”升级为可执行的四层视觉模型：

| 层 | 作用 | 作用范围 |
|:--|:--|:--|
| 风格 `style` | 字体、网格、几何、材质、图片、图标和图表语言 | 整套锁定 |
| 页面类型 `page_type` | 封面、架构、流程、详解、案例、实施计划等构图语法 | 每页变化 |
| 行业视觉 `industry` | 港口/金融/制造相关的几何、素材和视觉语气 | 整套锁定 |
| 语义配色 `palette` | 背景、表面、结构、聚焦、文字、边界和状态色 | 整套锁定 |

### 12 套语义配色

| 配色 | 层级 | 结构色 / 聚焦色 | 典型方向 |
|:--|:--|:--|:--|
| `orange-teal` | Core | 深青绿 / 橙 | 公司默认、港口、综合方案 |
| `finance-navy-teal` | Core | 藏青 / 深青绿 | 银行、保险、金融科技 |
| `industrial-navy-orange` | Core | 工业藏青 / 安全橙 | 汽车、制造、工业 AI |
| `ink-paper` | Core | 深墨 / 藏青 | 咨询、案例、研究 |
| `swiss-ikb` | Core | 近黑 / IKB 蓝 | 科技发布、数据演讲 |
| `graphite-cobalt` | Core | 石墨 / 钴蓝 | 克制通用科技、AI、产品 |
| `liantong-red` | Brand | 深灰 / 品牌红 | 对应品牌体系 |
| `navy-gold` | Conditional | 藏青 / 金 | 正式高层汇报 |
| `forest-ivory` | Conditional | 森林绿 / 陶土 | 绿色港口、低碳制造、ESG |
| `deep-space` | Specialized | 深藏青 / 荧光青 | 专用深色 HUD |
| `tech-blue` | Legacy | 深蓝 / 科技蓝 | 旧科技稿兼容 |
| `warm-orange` | Legacy | 暖深色 / 橙 | 旧暖调叙事稿兼容 |

每套配色定义 16 个语义角色。聚焦/状态填充色与浅底可读文字色分开；验证器会检查主要文字、
聚焦文字、状态文字和反相文字的对比度。

### 9 种风格

| 风格 | 层级 | 视觉语言 | 信息密度 |
|:--|:--|:--|:--|
| `swiss-grid` | Core | 12 栏、直角、发丝线、单一锚点色 | 中 |
| `industrial-diagram` | Core | 工程网格、正交连接、设备线描 | 中高 |
| `flat-editorial` | Core | 编辑留白、大字号、平面色块 | 低中 |
| `product-evidence` | Core | 主证据面、窄注释栏、来源带 | 中 |
| `lineart-minimal` | Conditional | 单色细线、一个主线描、大留白 | 低 |
| `illust-2.5d` | Conditional | 等距插画、旅程路径 | 中低 |
| `card-modern` | Conditional | 非对称模块、折角、超大数字 | 中 |
| `glass-3d` | Specialized | 玻璃分层、等距系统 | 高 |
| `hud-frame` | Specialized | 深底线框、真实参数 | 中高 |

7 个风格各有 3 张 1600×900 中性参考图；`swiss-grid` 和 `industrial-diagram` 使用完整
文字骨架。参考图不含文字、品牌、Logo、客户、日期、版本或数据，不会把旧实例内容带进新项目。

### 11 类页面构图

`cover`、`toc`、`section`、`overview`、`architecture`、`flow`、`detail`、
`compare-kpi`、`case`、`roadmap`、`closing`。

同一套 PPT 不靠换风格制造变化，而是让不同页面类型在统一标题轴、边距、字体、图形和配色角色下，
采用适合自己的构图。旧 `cover/content/arch/...` template 会自动映射，无需重写旧计划。

### 4 个行业视觉修饰器

| 行业 | 默认建议 | 只改变什么 |
|:--|:--|:--|
| 通用 `general` | `orange-teal × swiss-grid` | 中性商务视觉 |
| 港口 `port-terminal` | `orange-teal × industrial-diagram` | 堆场网格、路径、设备线描、宽幅构图 |
| 金融 `finance` | `finance-navy-teal × flat-editorial` | 制度化网格、发丝线、克制图表 |
| 汽车制造 `automotive-manufacturing` | `industrial-navy-orange × industrial-diagram` | 装配网格、工程线、设备/零件轮廓 |

行业修饰器不自动规划行业内容。客户品牌 > 公司品牌 > 行业兜底；例如客户有明确 VI 时，
金融行业也不会强行换成金融藏青绿。

完整组合、冲突原因、参考来源映射和扩展规则见 `references/design/INDEX.md`。
兼容性由 `references/design/compatibility.json` 执行；新增资源后运行
`python scripts/validate_design.py`，未登记或不完整的资源不会放行。

---

## 生图后端

| 运行环境 | 默认调用 | 默认模型 | 凭据 |
|:--|:--|:--|:--|
| **AGY CLI** | 原生 `generate_image` | `gemini-3.1-flash-image`（Nano Banana 2） | AGY 登录会话 |
| **Codex** | 原生 `image_gen` | `gpt-image-2` | Codex / ChatGPT 登录会话 |
| **其他客户端** | Gemini REST API | `gemini-3.1-flash-image` | `GEMINI_API_KEY` 或 `GOOGLE_API_KEY` |

路由看的是当前宿主提供的原生工具，而不是“电脑上还安装了哪些 CLI”：

- 在 AGY 中不会要求额外 Google API key，直接使用 `generate_image`；
- 在 Codex 中不会因为发现 AGY 可执行文件就绕到 AGY，继续使用 Codex 原生 ImageGen；
- 其他客户端必须配置 Gemini API key，默认不再抢先调用本机 Codex CLI；
- `agy/cli` 与 `codex/cli` 仅作为用户显式指定的兼容桥。当前 `agy -p` 必须先通过
  preflight；无输出时直接失败，不会偷偷换成 Codex 或 Gemini API。

Phase 4 把 `provider`、`image_transport`、`image_model` 锁入 `plan.json`。第一张样张开始后，
同一套 PPT 不允许临时改单页后端或在失败时静默切换。确需整体换模型，应先运行
`plan_tool.py provider`，再重生成受影响页面。

AGY 原生工具当前没有独立参考图参数；PPT Creator 会继续使用完整风格提示词、设计样张和逐页
QA 保证一致性。Gemini API 和 Codex 能力允许时仍会提交风格参考图。

**API key 只通过环境变量提供，禁止粘贴到对话中，也不会写入计划文件或日志。**

### 从 v2.2.0 升级到 v2.3.0

- 旧页面 `template` 自动映射为 11 类标准 `page_type`，原字段继续保留；
- 旧计划自动使用 `industry=general`，不会擅自增加行业内容；
- 旧 6 套配色和 6 种风格全部保留，旧合法组合继续可用；
- 新增 5 套配色、2 种风格、11 类页面视觉片段和 4 个行业视觉修饰器；
- 自定义 palette 升级到当前版本需要补齐 16 个语义 Token；自定义 style 需要增加整套风格骨架。

### 从 v2.3.0 升级到 v2.4.0

- 旧 plan 自动补 `schema_version=2.4`、`assurance_profile=standard` 和
  `delivery_mode=raster_slide`；
- 已进入 prompted/generated/approved 的旧页面采用当前输入为哈希基线，不会因升级全部重做；
- 新增项目契约、来源/素材真实性、变更自动失效、精确页面复用和最终同步 gate；
- 新增可选 OCR 文本核验；没有 OCR 能力的客户端仍可正常运行；
- `build_ppt.py` 自动生成最终 Markdown 大纲与 JSON 交付清单；
- 七阶段、四层视觉系统、图片确认预算和生图后端路由保持不变。

### 从 v2.4.0 升级到 v2.5.0

- plan schema 保持 2.4，不需要迁移现有页面内容或重新确认大纲；
- `tech-blue`、`warm-orange` 和既有合法组合继续可用，但会显示 Legacy 提醒；
- 新增 `graphite-cobalt`、`product-evidence` 和 20 个相应交叉组合；
- palette 新增 4 个可读文字 Token；旧 palette 已全部补齐；
- 旧 18 张参考图替换为中性生成资产，并新增 3 张产品证据参考图；
- Phase 4/7 新增 `verify_design_plan.py`，warning 不自动阻止用户已明确选择的专项风格；
- 事实契约、生图后端、图片确认预算和 raster-slide 交付方式保持不变。

更早版本的生图后端字段仍按以下规则迁移：

- 旧 `provider=gemini` 自动迁移为 `gemini/api/gemini-3.1-flash-image`；
- 旧 `provider=codex` 保持为 `codex/cli/gpt-image-2`；
- 旧 `provider=codex-builtin` 自动迁移为 `codex/native/gpt-image-2`；
- 新建计划必须明确锁定 provider/transport/model，旧计划的其他字段不会被改写。

---

## 安装

```bash
git clone https://github.com/sunfeihu007/ppt-creator.git
pip install -r ppt-creator/requirements.txt   # python-pptx, Pillow
```

已有本地副本时，可在仓库目录中升级到 GitHub 最新版本：

```bash
git switch main
git pull --ff-only origin main
pip install -r requirements.txt
```

放入对应 agent 的 skills 目录：

| Agent | 位置 |
|:--|:--|
| AGY CLI | `~/.agents/skills/ppt-creator/` |
| Claude Code | `~/.claude/skills/ppt-creator/` |
| Cowork（Claude 桌面端） | 设置 → Capabilities → 安装 skill（或导入 .skill 包） |
| Codex CLI / Codex 桌面端 | 项目 `.codex/skills/ppt-creator/` 或全局 `~/.codex/skills/ppt-creator/` |
| Hermes Agent | `~/.hermes/skills/ppt-creator/` |
| OpenClaw | 任一已配置 skills 根目录 |

**Codex 用户建议**在 AGENTS.md 加一句，防止内置生图工具绕过流程：

```
制作PPT必须使用 ppt-creator skill 的七步流程（以 ppt_workspace/plan.json 为准），
禁止绕过流程直接用 image_gen 单发生成幻灯片图片。
```

## 使用

对 agent 说：

> 帮我做一个给投资人看的产品介绍 PPT，15 分钟

然后跟着七步走即可。中断后说"继续做 PPT"，agent 会从 plan.json 恢复进度。

**脚本层直接调用**（调试/自动化）：

```bash
python scripts/plan_tool.py init --file draft_plan.json          # 建立计划
python scripts/plan_tool.py contract --file contract.json       # 更新需求/声明/来源
python scripts/plan_tool.py lint --ids all                      # 生图前语义校验
python scripts/plan_tool.py sync                                # 变更后失效旧产物
python scripts/plan_tool.py sync-check                          # 检查产物是否仍匹配
python scripts/plan_tool.py reuse --id P12 --from P02           # 精确复用页面
python scripts/plan_tool.py export-outline                      # 从plan导出最终大纲
python scripts/plan_tool.py design --palette orange-teal --style industrial-diagram \
  --industry port-terminal --provider agy --transport native       # AGY 港口方案
python scripts/plan_tool.py design --palette finance-navy-teal --style flat-editorial \
  --industry finance --provider codex --transport native           # Codex 金融方案
python scripts/plan_tool.py design --palette industrial-navy-orange \
  --style industrial-diagram --industry automotive-manufacturing \
  --provider gemini --transport api                                # 其他客户端制造方案
python scripts/plan_tool.py status                               # 随时看进度
python scripts/make_prompt.py --page P01 --print                 # 拼装提示词
python scripts/gen_image.py --page P01 --provider gemini --transport api
python scripts/gen_image.py --page P01 --provider agy --transport native \
  --import-file /absolute/path/to/agy-output.jpg                  # 导入原生产物
python scripts/validate_design.py                                # 校验全部视觉资源与108个组合
python scripts/verify_design_plan.py                             # 检查组合与整套版式节奏
python scripts/generate_style_refs.py --check                    # 校验21张中性参考图
python scripts/verify_pages.py                                   # 机器校验
python scripts/verify_semantics.py                               # 可选OCR语义校验
python scripts/build_ppt.py                                      # gate→压缩→组装→备注
```

---

## 目录结构

```
ppt-creator/
├── SKILL.md                      # 技能主定义（七步总览+第一原则）
├── references/
│   ├── constraints.md            # 全局约束（自动附加到每条生图提示词）
│   ├── project-contract.md       # 事实契约、来源、变更同步与OCR规则
│   ├── phases/                   # Phase 1-7 详细指令（按需加载）
│   └── design/                   # 四层视觉系统
│       ├── governance.json       # 风格/配色分级与整套视觉锁
│       ├── compatibility.json    # 12×9完整组合
│       ├── reference-manifest.json # 21张中性参考图清单与哈希
│       ├── palettes/             # 12套语义配色
│       ├── styles/               # 9种整套风格骨架（7种含中性参考图）
│       ├── page-types/           # 11类单页构图片段
│       └── industries/           # 4类纯视觉行业修饰
├── scripts/
│   ├── plan_tool.py              # 状态/契约/变更失效/复用/同步 gate
│   ├── project_contract.py       # 通用 schema、hash、lint 与大纲导出
│   ├── make_prompt.py            # 四层视觉+内容+约束的提示词拼装
│   ├── design_governance.py      # 组合分级、版式族与节奏检查
│   ├── verify_design_plan.py     # Phase 4/7整套视觉预检
│   ├── generate_style_refs.py    # 可复现中性参考图生成/校验
│   ├── image_providers.py        # Gemini API + 显式 AGY/Codex CLI 适配器
│   ├── gen_image.py              # 路由锁定/重试/原生产物导入/16:9裁切
│   ├── verify_pages.py           # 产物校验（存在/可打开/比例/分辨率）
│   ├── verify_semantics.py       # 可选OCR文本与契约核验
│   └── build_ppt.py              # gate→图片压缩→组装→注入演讲备注
├── tests/                         # 路由、兼容迁移、凭据安全与图片导入测试
└── evals/evals.json               # 行为评测用例
```

## 质量保障

- **提示词脚本化拼装**：风格骨架、页面类型、行业视觉、语义配色、禁止项全部固定，
  AI 只填每页的标题/要点，
  从机制上杜绝"越画越跑偏"；
- **全局约束**（`references/constraints.md`）：禁止色值/颜色名入画、禁止占位符与假 logo、
  禁止乱码、禁止风格漂移、软性描述不承诺具体百分比；
- **双重校验**：脚本查比例/分辨率/损坏，AI 目检查乱码/截断/漂移；
- **语义与同步校验**：prompt 前查必需词/禁止词/证据边界，OCR 可用时复核实际页面；
  build 前再验证所有图片仍对应当前 plan；
- **自动压缩**：>2MB 的页面图组装时转 JPEG，成品体积缩小 5-20 倍，方便邮件/IM 分发。

## 模型使用建议

规划与内容创作：深度内容用顶级模型，常规汇报次顶级足够；提示词环节已脚本化，对模型
档位不敏感；生图选中文渲染准确的图像模型，草稿低档、定稿高档；目检 QA 用便宜的多模态
模型即可。

## Roadmap

- `editable_native / hybrid`：独立的原生可编辑渲染管线，不以修改字段冒充可编辑能力
- 输出 profiles、分辨率链路和生成成本/重试台账
- 行业视觉修饰器的样张基准图与像素级视觉回归评测
- 更多页面类型变体与端到端 evals 扩充

## License

MIT — see [LICENSE](LICENSE).
