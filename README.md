# PPT Creator —— 结构化演示文稿生成 Skill

> 当前版本 v2.3.0 · MIT License

一个面向 AI Agent 的 PPT 制作技能：与你对话式地规划大纲和内容，按升级后的
“风格 × 页面类型 × 行业视觉 × 语义配色”四层系统，用 AI 并行生成、逐页质检高质量幻灯片图片，
最终组装成带演讲者备注、可直接演示的 PPTX 文件。

兼容所有支持 Agent Skills（SKILL.md）标准的 agent：**AGY CLI、Codex CLI / Codex 桌面端、
Claude Code / Cowork、Hermes Agent、OpenClaw** 等。

---

## 它能做什么

- **对话式规划**：不是拿到一句话就开画，而是先和你讨论清楚——给谁看、讲多久、分几个
  部分、每页讲什么，确认后才动手；
- **四层设计系统**：11 套语义配色 × 8 种风格（88 个显式校验组合）＋11 类页面构图＋
  4 个行业视觉修饰器；支持客户品牌、公司品牌和行业兜底的明确优先级；
- **并行 AI 生图**：多页任务默认至少4个子 agent 并行生成 16:9 高清整图，玻璃拟态 3D、杂志排版、
  极简线描、科幻 HUD 等质感均可；
- **演讲者备注**：每页自动写入带时长标注的演讲备注（重点页 5-6 分钟/过渡页 1-2 分钟，
  含互动与转折提示）；
- **工程化流程**：七步流程状态化管理，中断可恢复、换 agent 可接续；产物自动校验、
  自动压缩，成品直接可分发。
- **低干预确认**：图片阶段默认只确认设计样张和全套总览；有返工时最多增加一次，总计不超过3次。

## 当前版本亮点

- **状态化七步流程**：`plan.json` 记录阶段、页面和设计状态，任务中断后可继续；
- **四层视觉组合**：整套风格 × 单页页面类型 × 整套行业修饰 × 整套语义配色；
- **11 × 8 兼容矩阵**：88 个基础组合全部显式登记，冲突组合附原因和替代方案；
- **行业只修饰视觉**：港口、金融、汽车制造只改变图形、素材和视觉语气，不介入内容规划；
- **旧计划无痛迁移**：旧 template 自动映射标准页面类型，旧计划默认使用通用行业修饰；
- **宿主原生生图**：AGY 默认调用原生 Gemini Nano Banana 2，Codex 默认调用原生 ImageGen；
- **其他客户端直连 Gemini**：使用 API key 调用稳定版 `gemini-3.1-flash-image`；
- **整套模型锁定**：provider、transport、model 写入计划，禁止中途静默换模型或混用；
- **显式兼容桥**：保留 AGY CLI 与 Codex CLI 桥接，但不参与默认路由；
- **交付质量保障**：生成前有全局约束，生成后经过机器校验、人工目检和组装 gate。

## 适用场景

企业技术方案、产品介绍、立项汇报、培训课件、学术报告、销售交流。
对话中说"做个 PPT / 帮我做个汇报 / 生成演示文稿"即可触发。

---

## 七步工作流

| Phase | 做什么 | 产出 |
|:--|:--|:--|
| 1 大纲讨论 | 场景/受众/时长 → 3-5 个主要部分 | 大纲框架 |
| 2 内容方向 | 每部分 2-4 个核心要点，理顺逻辑 | 内容规划 |
| 3 页数分配 | 逐页清单（每页一个核心观点） | `plan.json` |
| 4 设计确定 | 品牌优先级 → 配色 → 风格 → 行业视觉修饰 → 生图后端 | 完整视觉锁定 |
| 5 框架页 | 样张确认后并行生成；AI逐页质检 | 框架页图片 |
| 6 内容页 | 至少4路并行生成 + AI目检 + 全套合并确认 | 全部页面图片 |
| 7 整合输出 | 校验 → 压缩 → 组装 → 注入备注 | 最终 PPTX |

**防跳步机制**：进度写入 `ppt_workspace/plan.json`（唯一事实来源），页面用 `qa_passed`
区分AI质检与用户批准，图片确认预算也持久化。`build_ppt.py` 仍拒绝组装任何未确认页面。

**合并返工语义**：全套总览中若只点名少数页面修改，其他已通过AI质检的页面立即视为批准，
只有点名页面退回重做；返工结果统一放在第3次、也是最后一次图片确认中。

---

## 四层视觉系统

v2.3 把“选一套颜色＋选一种质感”升级为可执行的四层视觉模型：

| 层 | 作用 | 作用范围 |
|:--|:--|:--|
| 风格 `style` | 字体、网格、几何、材质、图片、图标和图表语言 | 整套锁定 |
| 页面类型 `page_type` | 封面、架构、流程、详解、案例、实施计划等构图语法 | 每页变化 |
| 行业视觉 `industry` | 港口/金融/制造相关的几何、素材和视觉语气 | 整套锁定 |
| 语义配色 `palette` | 背景、表面、结构、聚焦、文字、边界和状态色 | 整套锁定 |

### 11 套语义配色

| 配色 | 结构色 / 聚焦色 | 典型方向 |
|:--|:--|:--|
| `orange-teal` | 深青绿 / 橙 | 公司默认、港口、综合方案 |
| `liantong-red` | 深灰 / 品牌红 | 运营商品牌 |
| `tech-blue` | 深蓝 / 科技蓝 | 通用科技与 AI |
| `navy-gold` | 藏青 / 金 | 正式高层汇报 |
| `warm-orange` | 暖深色 / 橙 | 亲和叙事 |
| `deep-space` | 深藏青 / 荧光青 | 专用深色 HUD |
| `finance-navy-teal` | 藏青 / 深青绿 | 银行、保险、金融科技 |
| `industrial-navy-orange` | 工业藏青 / 安全橙 | 汽车、制造、工业 AI |
| `ink-paper` | 深墨 / 藏青 | 咨询、案例、研究 |
| `swiss-ikb` | 近黑 / IKB 蓝 | 科技发布、数据演讲 |
| `forest-ivory` | 森林绿 / 陶土色 | 绿色港口、低碳制造、ESG |

每套配色都定义 12 个语义角色，避免“主色、辅色随便换”的问题。聚焦色只突出一个决定性对象；
成功、警告、风险色只有内容确实表达状态时才能使用。

### 8 种风格

| 风格 | 视觉语言 | 信息密度 |
|:--|:--|:--|
| `glass-3d` | 玻璃分层、等距结构 | 高 |
| `flat-editorial` | 编辑留白、大字号、平面色块 | 低中 |
| `lineart-minimal` | 单色细线、大留白 | 低 |
| `illust-2.5d` | 等距插画、几何纹样 | 中低 |
| `card-modern` | 现代模块、折页卡、超大数字 | 中 |
| `hud-frame` | 深底发光线框、扫描与参数标签 | 中高 |
| `swiss-grid` | 12 栏、直角、发丝线、单一锚点色 | 中 |
| `industrial-diagram` | 工程网格、正交连接、设备线描 | 中高 |

旧六种风格附 3 张真实版式参考图；`swiss-grid` 和 `industrial-diagram` 使用完整文字骨架。
没有参考图时不会虚构垫图参数。

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
- 自定义 palette 需要补齐 12 个语义 Token；自定义 style 建议增加整套风格骨架。

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
python scripts/validate_design.py                                # 校验全部视觉资源与88个组合
python scripts/verify_pages.py                                   # 机器校验
python scripts/build_ppt.py                                      # gate→压缩→组装→备注
```

---

## 目录结构

```
ppt-creator/
├── SKILL.md                      # 技能主定义（七步总览+第一原则）
├── references/
│   ├── constraints.md            # 全局约束（自动附加到每条生图提示词）
│   ├── phases/                   # Phase 1-7 详细指令（按需加载）
│   └── design/                   # 四层视觉系统
│       ├── palettes/             # 11套语义配色
│       ├── styles/               # 8种整套风格骨架（旧6种含参考图）
│       ├── page-types/           # 11类单页构图片段
│       └── industries/           # 4类纯视觉行业修饰
├── scripts/
│   ├── plan_tool.py              # plan.json 状态管理 + 防跳步 gate
│   ├── make_prompt.py            # 四层视觉+内容+约束的提示词拼装
│   ├── image_providers.py        # Gemini API + 显式 AGY/Codex CLI 适配器
│   ├── gen_image.py              # 路由锁定/重试/原生产物导入/16:9裁切
│   ├── verify_pages.py           # 产物校验（存在/可打开/比例/分辨率）
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
- **自动压缩**：>2MB 的页面图组装时转 JPEG，成品体积缩小 5-20 倍，方便邮件/IM 分发。

## 模型使用建议

规划与内容创作：深度内容用顶级模型，常规汇报次顶级足够；提示词环节已脚本化，对模型
档位不敏感；生图选中文渲染准确的图像模型，草稿低档、定稿高档；目检 QA 用便宜的多模态
模型即可。

## Roadmap

- `build_native_ppt.py`：无生图后端时用 python-pptx 原生绘制（首选 flat-editorial 风格）
- 行业视觉修饰器的样张基准图与视觉回归评测
- 更多页面类型变体与端到端 evals 扩充

## License

MIT — see [LICENSE](LICENSE).
