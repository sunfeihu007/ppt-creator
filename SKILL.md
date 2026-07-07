---
name: ppt-creator
description: |
  结构化PPT生成技能：对话式规划大纲与内容，按"配色×风格"设计系统用AI生成页面图片，
  组装为带演讲者备注的PPTX。当用户提到"做PPT"、"生成演示文稿"、"制作幻灯片"、
  "帮我做个汇报/方案/课件"时触发。支持从文件夹/文档提取素材。
  共7个Phase，必须按顺序执行、逐一经用户确认，禁止跳步或合并；
  进度以 ppt_workspace/plan.json 为唯一事实来源。
version: 2.0.0
# Powered by MrSuperOne
---

# PPT Creator —— 结构化演示文稿生成（v2）

## 第一原则：状态文件

**任何时候开始或恢复工作，先读 `ppt_workspace/plan.json` 决定下一步；每完成一步立即用
`scripts/plan_tool.py` 更新状态。** 上下文丢失、会话中断、换 agent 后，一切以 plan.json 为准。
plan.json 不存在 = 从 Phase 1 开始。

## 七步工作流（顺序执行，禁止跳步）

| Phase | 名称 | 进入条件 | 完成条件（需用户确认） | 详细指令 |
|:---|:---|:---|:---|:---|
| 1 | 大纲讨论 | — | 主题/受众/页数/3-5个主要部分确定 | `references/phases/phase1-3-planning.md` |
| 2 | 内容方向 | 1 done | 每部分2-4个要点确定 | 同上 |
| 3 | 页数分配 | 2 done | 逐页清单确定，`plan_tool.py init` 生成 plan.json | 同上 |
| 4 | 设计确定 | 3 done | 配色+风格+生图后端写入 plan.json | `references/phases/phase4-design.md` |
| 5 | 框架页 | 4 done | 封面/目录/过渡/结束页生成并确认 | `references/phases/phase5-6-generation.md` |
| 6 | 内容页 | 5 done | 全部内容页生成、目检、用户确认 | 同上 |
| 7 | 整合输出 | 6 done | verify 通过、组装PPTX、备注完整 | `references/phases/phase7-assembly.md` |

进入每个 Phase 前，**必须先 Read 对应的 phases 文件**。在完成 Phase N 并获得用户确认前，
禁止进入 Phase N+1。`build_ppt.py` 内置 gate：页面未全部 approved 会拒绝组装。

## 脚本速查（所有确定性操作用脚本，禁止手写代码）

```bash
python scripts/plan_tool.py init --file draft_plan.json   # Phase 3: 创建 plan.json
python scripts/plan_tool.py status                        # 查看进度与下一步
python scripts/plan_tool.py phase --name 4_design --status done
python scripts/plan_tool.py page --id P01 --status approved
python scripts/make_prompt.py --page P01                  # 拼装提示词(骨架来自设计系统)
python scripts/gen_image.py --page P01                    # 生图(自动探测后端,带重试/裁切)
python scripts/verify_pages.py                            # 校验全部页面(尺寸/比例/损坏)
python scripts/build_ppt.py                               # gate检查→压缩→组装→注入备注
```

依赖：`pip install -r requirements.txt`（python-pptx、Pillow）。

## 设计系统（配色 × 风格解耦）

- 配色定义：`references/design/palettes/*.md`（颜色 Token + 提示词配色描述段）
- 风格定义：`references/design/styles/*.md`（质感版式，颜色无关）+ `ref-*.jpg` 版式参考图
- 组合矩阵与默认组合：`references/design/INDEX.md`（Phase 4 必读）
- 提示词 = 风格模板 + 配色描述段 + 页面内容 + 全局约束，由 `make_prompt.py` 拼装，
  AI 只提供每页的标题/要点/呈现方式，禁止手写完整提示词
- 垫图：风格参考图随生图请求一并提交，并声明"仅参考版式与质感，配色以文字为准"

## 生图后端（探测顺序）

1. **Codex 环境内**：直接使用内置 image_gen 工具（gpt-image-2，$imagegen），按提示词文件
   逐页生成 1920×1080，保存到 plan.json 指定路径，仍走 plan/verify 流程；
2. **GEMINI_API_KEY / GOOGLE_API_KEY 存在** → `gen_image.py --provider gemini`；
3. **本地安装了 codex CLI**（非 Codex 环境，如 Claude Code）→ `gen_image.py --provider codex`
   （通过 `codex exec` 调用 gpt-image-2，走 ChatGPT 订阅鉴权，无需 OpenAI API key）；
4. 都不可用 → 告知用户，建议配置 Gemini key 或安装 codex CLI。

**禁止**让用户把 API key 粘贴到对话中；key 只通过环境变量提供。
整套 PPT 锁定同一后端，中途不得切换（画风会断裂）。

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

## 演讲者备注

每页备注写入 plan.json 的 `notes` 字段，组装时自动注入。要求：开头标注建议时长
（重点页5-6分钟/普通页3-4分钟/过渡页1-2分钟），关键页加【互动】【关键转折】提示。

## 对话模式

引导式提问、结构化输出、关键决策点必须用户确认、允许随时回改已确定内容
（回改后用 plan_tool.py 同步状态，受影响页面状态退回 pending）。
