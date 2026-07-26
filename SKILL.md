---
name: ppt-creator
description: |
  结构化PPT生成技能：对话式规划大纲与内容，按"风格×页面类型×行业视觉×语义配色"
  四层设计系统用AI生成页面图片，
  组装为带演讲者备注的PPTX。当用户提到"做PPT"、"生成演示文稿"、"制作幻灯片"、
  "帮我做个汇报/方案/课件"时触发。支持从文件夹/文档提取素材。
  当用户要求从网站截图、PPT截图或设计链接扩展本技能的配色、风格或单页布局时也触发。
  复杂方案支持事实约束、来源追踪、变更自动失效、同图复用和最终同步校验。
  共7个Phase，按顺序执行；图片制作默认只进行设计样张和全套总览两次合并确认，返工时最多增加一次，
  总计不得超过3次；多页生图默认由至少4个子agent并行。进度以ppt_workspace/plan.json为准。
---

# PPT Creator —— 结构化演示文稿生成（v2.6.0）

## 第一原则：项目事实源

**任何时候开始或恢复工作，先读 `ppt_workspace/plan.json` 决定下一步；每完成一步立即用
`scripts/plan_tool.py` 更新状态。** 上下文丢失、会话中断、换 agent 后，一切以 plan.json 为准。
plan.json 不存在 = 从 Phase 1 开始。plan.json 同时保存当前需求决策、声明边界、来源引用、
页面依赖和产物哈希；不要把已被用户否定的表述只留在对话历史中。

客户方案、售前、案例、合规或含量化承诺的 PPT，在 Phase 1–3 必读
`references/project-contract.md`。普通内部汇报使用 `standard`；客户交付使用
`client-facing`；案例、金融、招投标或事实敏感材料使用 `evidence-sensitive`。
三种等级只改变校验强度，不改变内容大纲，也不增加用户确认点。

## 七步工作流（顺序执行，禁止跳步）

| Phase | 名称 | 进入条件 | 完成条件 | 详细指令 |
|:---|:---|:---|:---|:---|
| 1 | 大纲讨论 | — | 主题/受众/页数/3-5个主要部分确定 | `references/phases/phase1-3-planning.md` |
| 2 | 内容方向 | 1 done | 每部分2-4个要点确定 | 同上 |
| 3 | 页数分配 | 2 done | 逐页清单确定，`plan_tool.py init` 生成 plan.json | 同上 |
| 4 | 设计确定 | 3 done | 视觉锁写入 plan.json，整套视觉预检通过 | `references/phases/phase4-design.md` |
| 5 | 框架页 | 4 done | 样张确认；其余框架页生成并通过AI质检 | `references/phases/phase5-6-generation.md` |
| 6 | 内容页 | 5 done | 全部内容页生成、目检、合并确认 | 同上 |
| 7 | 整合输出 | 6 done | 页面/语义/同步 gate 通过，PPTX/大纲/清单完整 | `references/phases/phase7-assembly.md` |

进入每个 Phase 前，**必须先 Read 对应的 phases 文件**。禁止跳过前置 gate，但不要把 Phase
边界变成额外用户确认；Phase 5 框架页达到 `qa_passed` 后可进入 Phase 6。`build_ppt.py`
仍要求最终全部 `approved`。

## 脚本速查（所有确定性操作用脚本，禁止手写代码）

```bash
python scripts/plan_tool.py init --file draft_plan.json   # Phase 3: 创建 plan.json
python scripts/plan_tool.py contract --file contract.json # 更新需求/声明/来源
python scripts/plan_tool.py lint --ids all                # 生图前语义检查
python scripts/plan_tool.py sync                          # 变更后自动失效受影响页
python scripts/plan_tool.py sync-check                    # 组装前检查新旧产物漂移
python scripts/plan_tool.py reuse --id P12 --from P02     # 精确复用同一页面资产
python scripts/plan_tool.py status                        # 查看进度与下一步
python scripts/plan_tool.py phase --name 4_design --status done
python scripts/plan_tool.py design --palette orange-teal --style industrial-diagram \
  --industry port-terminal --provider codex --transport native
python scripts/plan_tool.py page --id P01 --status approved
python scripts/plan_tool.py pages --ids P02,P03 --status qa_passed
python scripts/plan_tool.py review --type full-deck --ids all --result approved
python scripts/make_prompt.py --page P01                  # 拼装提示词(骨架来自设计系统)
python scripts/verify_design_plan.py                      # 组合/层级/整套版式节奏预检
python scripts/intake_visual_reference.py --help          # 截图/网址先建候选，不直接污染注册表
python scripts/generate_palette_preview.py --help         # 生成封面/架构/详解三页配色样张
python scripts/gen_image.py --page P01                    # 非原生客户端脚本生图
python scripts/gen_image.py --page P01 --provider agy --transport native \
  --import-file /absolute/path/to/agy-output.jpg           # 导入AGY原生产物
python scripts/verify_pages.py                            # 校验全部页面(尺寸/比例/损坏)
python scripts/verify_semantics.py                        # 有OCR文本时核对标题/术语/声明
python scripts/build_ppt.py                               # gate检查→压缩→组装→注入备注
```

依赖：`pip install -r requirements.txt`（python-pptx、Pillow）。

## 四层视觉系统（风格 × 页面类型 × 行业修饰 × 语义配色）

- 整套 `style`：9 种风格家族，控制字体、网格、材质、几何、图片、图标和图表语言；
- 单页 `page_type`：11 类页面构图，控制封面、架构、流程、详解、案例、实施计划等视觉形式；
- 整套 `industry`：4 类行业视觉修饰，只控制图形、素材和视觉语气，不规划行业内容；
- 整套 `palette`：13 套语义配色，用背景/表面/结构/聚焦/可读文字/边界/状态角色替代随意套色；
- 完整规则、行业默认值、参考来源映射：`references/design/INDEX.md`（Phase 4 必读）；
- 用户提供截图、网站或 PPT 设计参考时，先读
  `references/design/visual-reference-intake.md`；单张截图只能建立配色或单页布局候选，
  不得直接注册成整套 style；
- 配色定义：`references/design/palettes/*.md`；页面类型：`references/design/page-types/`；
  行业视觉修饰：`references/design/industries/`；风格：`references/design/styles/*.md`；
- 机器兼容与治理：`references/design/compatibility.json`、`governance.json` 和
  `reference-manifest.json`；新增资源后必须运行 `python scripts/validate_design.py`
- 提示词 = 整套风格骨架 + 单页页面类型 + 整套行业视觉修饰 + 语义配色 + 页面内容 + 全局约束，
  由 `make_prompt.py` 拼装，
  AI 只提供每页的标题/要点/呈现方式，禁止手写完整提示词
- 旧 `template` 自动映射为标准 `page_type`，旧 plan 默认 `industry=general`，无需人工迁移；
- 垫图：有风格参考图时一并提交并声明"仅参考版式与质感，配色以文字为准"；没有参考图时
  使用完整风格骨架，禁止虚构工具参数。

锁定规则：整套 PPT 共享同一 `palette × style × industry × provider`；页面之间只通过
`page_type` 和 `layout_hint` 变化。品牌优先级为客户品牌 > 公司品牌 > 行业视觉兜底。

新项目优先 Core：`swiss-grid / industrial-diagram / flat-editorial / product-evidence`，
以及 `orange-teal / finance-navy-teal / industrial-navy-orange / ink-paper /
swiss-ikb / graphite-cobalt`。`glass-3d`、`hud-frame` 和 `deep-space` 是专项选择；
`porcelain-azure` 是产品、AI 和金融科技的明亮 Conditional 选择；
`tech-blue`、`warm-orange` 只保留旧稿兼容。选择 `specialized/legacy` 必须展示提醒，
`blocked` 必须拒绝。Phase 4 和 Phase 7 运行 `verify_design_plan.py`，检查连续同构版式和
重复三卡；不新增用户确认点。

每套 palette 定义 16 个语义角色。`FOCUS/STATUS_*` 用于色块、线和图标，小字必须使用
`FOCUS_TEXT/STATUS_*_TEXT`；`validate_design.py` 自动检查文字角色在背景/表面上的
4.5:1 对比度。带参考图的 7 个风格使用 21 张无文字、无品牌、无数据的中性参考图；
禁止从参考图复制任何可见内容。

`governance.json` 还会为九种 style 注入字体家族预算、字号层级、标题/正文/小字规则和
跨页空间锚点。`glass-3d` 最多两级透明材质，禁止玻璃叠玻璃；架构、流程、表格和密集对比页
必须把普通节点平面化，只保留一个玻璃焦点层。

## 生图后端（按宿主能力路由，整套锁定）

在 Phase 4 先判断当前 agent **实际拥有的原生工具**，不要靠猜测环境变量：

1. **AGY CLI 环境**：默认调用 AGY 原生 `generate_image`，锁定为
   `agy/native/gemini-3.1-flash-image`（Nano Banana 2）。不要求 Google API key。
   当前原生工具没有独立参考图参数；提示词已包含完整风格骨架和配色规则，样张与逐页 QA
   继续作为一致性保障。工具保存图片后，用 `gen_image.py --import-file` 统一转 PNG、裁切和记账。
2. **Codex 环境**：默认调用 Codex 原生 `image_gen`（gpt-image-2），锁定为
   `codex/native/gpt-image-2`。不得因为本机安装了 AGY 而绕到 AGY CLI。
3. **其他客户端**：默认使用 `gen_image.py --provider gemini --transport api`，要求
   `GEMINI_API_KEY` 或 `GOOGLE_API_KEY`；稳定默认模型为 `gemini-3.1-flash-image`。
4. **显式兼容桥**：只有用户明确要求时才使用 `agy/cli` 或 `codex/cli`。AGY CLI 桥会先验证
   `agy -p` 是否返回可用结果；失败时直接停止，不静默切换模型。

Phase 4 必须把 `provider`、`image_transport`、`image_model` 写入 plan.json。样张开始后：

- 所有页面必须共享同一组 provider/transport/model；
- 显式参数不能覆盖锁定值，中途切换必须先用 `plan_tool.py provider` 正式更新状态，并重生成
  已完成页面；
- `both` 只允许在尚未锁定时做 CLI/API 预选对比，锁定后禁止使用；
- 任何后端失败都不得静默换用另一个后端继续剩余页面。

**禁止**让用户把 API key 粘贴到对话中；key 只通过环境变量提供，不写入 plan.json 或日志。

## 全局约束（每次生成提示词自动包含，违反即重做）

完整清单见 `references/constraints.md`，核心：

1. 禁止任何色值/颜色名以文字出现在画面上；
2. 禁止占位符（[汇报人]、[日期]）、假logo、假联系方式、"内部参考"类文字；
3. 禁止乱码汉字与捏造词汇，字体清晰可读；
4. 全篇统一风格、行业视觉和语义色角色；页面类型可以变，但标题轴、边距和图形语言不得漂移；
5. 聚焦色每页只突出一个决定性对象；状态色只表示真实成功/警告/风险；
6. 禁止通用 AI 大脑、机器人、彩虹图标和无关科幻装饰；
7. 禁止跨页重复三等分卡片/卡片墙；整套几何、圆角和阴影系统保持一致；
8. 软性描述效果，避免具体百分比承诺。

## 目检（Phase 6/7 强制）

每页生成后必须用视觉能力查看图片：乱码、文字截断、风格漂移、比例异常。
发现问题重新生成该页，最多3轮，仍失败则与用户讨论调整内容或换呈现方式。
宿主能提供 OCR 时，把逐页结果保存为 `ppt_workspace/qa/ocr/PXX.txt` 并运行
`verify_semantics.py`；OCR 是可选增强，禁止因为客户端没有 OCR 就伪造检查结果。

## 图片确认预算与并行生成（强制）

- 图片制作默认仅请求两次确认：①优先合并“封面+架构+详解/案例”代表性样张；②AI完成逐页
  质检后的全套总览。计划缺少某类页面时换最接近代表页；用户要求返工时才使用第③次合并确认，
  绝不创建第④次确认。
- 用 `plan_tool.py review` 记录真实图片确认；`plan.json.review` 是跨会话确认预算的事实来源。
- 全套确认只点名部分返工页时，未点名且已 `qa_passed` 的页面视为批准；只将点名页退回
  `pending`，避免第三次确认后仍有未批准页面。
- 不逐页确认内容或图片，不按2–4页分批打断用户。Phase 3 的逐页清单就是批量制作授权；仅在
  某页内容存在无法自行消解的重大歧义时提问。
- 除非用户明确要求单独生成/重做一页，否则待生成页≥4时必须派至少4个子agent并行生图；
  少于4页时派 `min(4, 待生成页数)` 个。保持至少4条队列持续取页，而非每4页重新派agent。
- 主agent先串行生成全部提示词，再按复杂度均衡分配页面。子agent只写各自图片文件，禁止写
  `plan.json`；使用脚本时加 `gen_image.py --no-state`。主agent收集结果后用 `plan_tool.py pages`
  原子化批量更新状态，避免并发覆盖。
- 所有子agent必须共享已锁定的 palette、style、industry、provider、语义色角色、页面类型注册表、
  参考图、全局约束和已确认样张；每页使用自己的 page_type，单页失败只重试该页，不阻塞其他队列。

## 演讲者备注

每页备注写入 plan.json 的 `notes` 字段，组装时自动注入。要求：开头标注建议时长
（重点页5-6分钟/普通页3-4分钟/过渡页1-2分钟），关键页加【互动】【关键转折】提示。

## 对话模式

引导式提问、结构化输出、关键决策点必须用户确认、允许随时回改已确定内容
（回改后运行 `plan_tool.py sync`，只把受影响页面退回 pending）。当前交付模式固定为
`raster_slide`（整页图片式 PPTX）；不得承诺文字和图形原生可编辑。
