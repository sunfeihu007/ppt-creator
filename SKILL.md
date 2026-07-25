---
name: ppt-creator
description: |
  结构化PPT生成技能：对话式规划大纲与内容，按"配色×风格"设计系统用AI生成页面图片，
  组装为带演讲者备注的PPTX。当用户提到"做PPT"、"生成演示文稿"、"制作幻灯片"、
  "帮我做个汇报/方案/课件"时触发。支持从文件夹/文档提取素材。
  共7个Phase，按顺序执行；图片制作默认只进行设计样张和全套总览两次合并确认，返工时最多增加一次，
  总计不得超过3次；多页生图默认由至少4个子agent并行。进度以ppt_workspace/plan.json为准。
---

# PPT Creator —— 结构化演示文稿生成（v2.2.0）

## 第一原则：状态文件

**任何时候开始或恢复工作，先读 `ppt_workspace/plan.json` 决定下一步；每完成一步立即用
`scripts/plan_tool.py` 更新状态。** 上下文丢失、会话中断、换 agent 后，一切以 plan.json 为准。
plan.json 不存在 = 从 Phase 1 开始。

## 七步工作流（顺序执行，禁止跳步）

| Phase | 名称 | 进入条件 | 完成条件 | 详细指令 |
|:---|:---|:---|:---|:---|
| 1 | 大纲讨论 | — | 主题/受众/页数/3-5个主要部分确定 | `references/phases/phase1-3-planning.md` |
| 2 | 内容方向 | 1 done | 每部分2-4个要点确定 | 同上 |
| 3 | 页数分配 | 2 done | 逐页清单确定，`plan_tool.py init` 生成 plan.json | 同上 |
| 4 | 设计确定 | 3 done | 配色+风格+生图后端写入 plan.json | `references/phases/phase4-design.md` |
| 5 | 框架页 | 4 done | 样张确认；其余框架页生成并通过AI质检 | `references/phases/phase5-6-generation.md` |
| 6 | 内容页 | 5 done | 全部内容页生成、目检、合并确认 | 同上 |
| 7 | 整合输出 | 6 done | verify 通过、组装PPTX、备注完整 | `references/phases/phase7-assembly.md` |

进入每个 Phase 前，**必须先 Read 对应的 phases 文件**。禁止跳过前置 gate，但不要把 Phase
边界变成额外用户确认；Phase 5 框架页达到 `qa_passed` 后可进入 Phase 6。`build_ppt.py`
仍要求最终全部 `approved`。

## 脚本速查（所有确定性操作用脚本，禁止手写代码）

```bash
python scripts/plan_tool.py init --file draft_plan.json   # Phase 3: 创建 plan.json
python scripts/plan_tool.py status                        # 查看进度与下一步
python scripts/plan_tool.py phase --name 4_design --status done
python scripts/plan_tool.py page --id P01 --status approved
python scripts/plan_tool.py pages --ids P02,P03 --status qa_passed
python scripts/plan_tool.py review --type full-deck --ids all --result approved
python scripts/make_prompt.py --page P01                  # 拼装提示词(骨架来自设计系统)
python scripts/gen_image.py --page P01                    # 非原生客户端脚本生图
python scripts/gen_image.py --page P01 --provider agy --transport native \
  --import-file /absolute/path/to/agy-output.jpg           # 导入AGY原生产物
python scripts/verify_pages.py                            # 校验全部页面(尺寸/比例/损坏)
python scripts/build_ppt.py                               # gate检查→压缩→组装→注入备注
```

依赖：`pip install -r requirements.txt`（python-pptx、Pillow）。

## 设计系统（配色 × 风格解耦）

- 配色定义：`references/design/palettes/*.md`（颜色 Token + 提示词配色描述段）
- 风格定义：`references/design/styles/*.md`（质感版式，颜色无关）+ `ref-*.jpg` 版式参考图
- 组合矩阵与默认组合：`references/design/INDEX.md`（Phase 4 必读）
- 机器兼容规则：`references/design/compatibility.json`；新增配色/风格后必须运行
  `python scripts/validate_design.py`，未登记组合不得默认放行
- 提示词 = 风格模板 + 配色描述段 + 页面内容 + 全局约束，由 `make_prompt.py` 拼装，
  AI 只提供每页的标题/要点/呈现方式，禁止手写完整提示词
- 垫图：风格参考图随生图请求一并提交，并声明"仅参考版式与质感，配色以文字为准"

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
4. 全篇统一"配色×风格"，禁止风格漂移；同类元素对齐，文字完整不截断；
5. 软性描述效果，避免具体百分比承诺。

## 目检（Phase 6/7 强制）

每页生成后必须用视觉能力查看图片：乱码、文字截断、风格漂移、比例异常。
发现问题重新生成该页，最多3轮，仍失败则与用户讨论调整内容或换呈现方式。

## 图片确认预算与并行生成（强制）

- 图片制作默认仅请求两次确认：①封面或“封面+代表性内容页”的合并设计样张；②AI完成逐页
  质检后的全套总览。用户要求返工时才使用第③次合并确认，绝不创建第④次确认。
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
- 所有子agent必须共享已锁定的 palette、style、provider、参考图、全局约束和已确认样张；
  单页失败只重试该页，不阻塞其他队列。

## 演讲者备注

每页备注写入 plan.json 的 `notes` 字段，组装时自动注入。要求：开头标注建议时长
（重点页5-6分钟/普通页3-4分钟/过渡页1-2分钟），关键页加【互动】【关键转折】提示。

## 对话模式

引导式提问、结构化输出、关键决策点必须用户确认、允许随时回改已确定内容
（回改后用 plan_tool.py 同步状态，受影响页面状态退回 pending）。
