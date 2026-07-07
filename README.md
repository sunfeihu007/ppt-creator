# PPT Creator —— 结构化演示文稿生成 Skill (v2)

> **Powered by MrSuperOne**

对话式规划大纲与内容 → 按"配色 × 风格"设计系统用 AI 生成页面图片 → 组装为带演讲者
备注的 PPTX。兼容 Claude Code / Codex CLI / Hermes Agent / OpenClaw 等支持
Agent Skills（SKILL.md）标准的 agent。

## v2 相对 v1 的核心变化

1. **七步流程状态化**：进度写入 `ppt_workspace/plan.json`，脚本内置 gate，
   任何 agent 都无法跳步（解决"七步变三步"问题）；
2. **代码脚本化**：生图/重试/裁切/校验/组装全部是 `scripts/` 下的可执行脚本，
   模型不再誊写代码；
3. **配色 × 风格解耦**：6 配色 × 6 风格自由组合（含兼容矩阵与版式参考图垫图机制）；
4. **双生图后端**：Gemini API（key 走环境变量+header）/ **本地 Codex CLI**
   （`codex exec` 调用内置 image_gen，gpt-image-2，走 ChatGPT 订阅鉴权，无需 OpenAI API key）；
5. **提示词由脚本拼装**：风格骨架+配色描述+全局约束固定，AI 只填内容变量，杜绝风格漂移。

## 目录结构

```
ppt-creator/
├── SKILL.md                     # 主定义（瘦身版，七步总览+第一原则）
├── references/
│   ├── constraints.md           # 全局约束（自动附加到每条提示词）
│   ├── phases/                  # 各 Phase 详细指令（按需加载）
│   └── design/                  # 设计系统
│       ├── INDEX.md             #   组合矩阵与默认组合
│       ├── palettes/*.md        #   6 配色（Token + 提示词配色描述段）
│       └── styles/*.md + ref-*.jpg  # 6 风格（颜色无关）+ 版式参考图
├── scripts/
│   ├── plan_tool.py             # plan.json 状态管理 + gate
│   ├── make_prompt.py           # 提示词拼装（配色×风格×页面内容×约束）
│   ├── gen_image.py             # 生图（gemini/codex 双后端，重试+16:9裁切）
│   ├── verify_pages.py          # 产物机器校验
│   └── build_ppt.py             # gate→压缩→组装→注入备注
└── evals/evals.json
```

## 安装

```bash
pip install -r requirements.txt   # python-pptx, Pillow
```

放入各 agent 的 skills 目录即可：

| Agent | 位置 |
|:---|:---|
| Claude Code / Cowork | `~/.claude/skills/ppt-creator/` |
| Codex CLI | 项目 `.codex/skills/` 或全局 skills 目录 |
| Hermes Agent | `~/.hermes/skills/ppt-creator/` |
| OpenClaw | 任一已配置的 skills 根目录下 |

**Codex 用户建议**在 AGENTS.md 加一句，防止内置生图工具"抢戏"：

```
制作PPT必须使用 ppt-creator skill 的七步流程（以 ppt_workspace/plan.json 为准），
禁止绕过流程直接用 image_gen 单发生成幻灯片图片。
```

## 生图后端

| 后端 | 条件 | 说明 |
|:---|:---|:---|
| Codex 环境内置 image_gen | 在 Codex CLI 中运行本 skill | 直接用 `$imagegen`（gpt-image-2），按 prompts/PXX.txt 生图 |
| Gemini API | `export GEMINI_API_KEY=...` | 模型默认 `gemini-3.1-flash-image-preview`，可用 `GEMINI_IMAGE_MODEL` 覆盖 |
| 本地 codex CLI | 已安装并登录 codex | `gen_image.py --provider codex`，走 ChatGPT 订阅鉴权，无需 OpenAI API key |

不要把 key 粘贴到对话中；key 只通过环境变量提供。整套 PPT 锁定同一后端。

## 快速体验（脚本层）

```bash
python scripts/plan_tool.py init --file draft_plan.json
python scripts/plan_tool.py design --palette hansheng-orange-green --style glass-3d --provider gemini
python scripts/make_prompt.py --page P01 --print
python scripts/gen_image.py --page P01
python scripts/verify_pages.py
python scripts/build_ppt.py --allow-generated
```

## 模型使用建议（人为配置，非 skill 强制）

- 规划与内容创作（Phase 1-3）：深度内容用顶级模型，常规汇报次顶级足够；
- 提示词已脚本化拼装，Phase 5-6 对模型档位不敏感；
- 生图：选中文文字渲染准确度高的图像模型；草稿可用低档，定稿统一高档重生成；
- 目检 QA：便宜多模态模型即可（如 Haiku 档 subagent 批量目检）。

## Roadmap

- `build_native_ppt.py`：无生图后端时用 python-pptx 原生绘制（首选 flat-editorial 风格）；
- 更多配色/风格；evals 端到端用例扩充。

## License

MIT — see [LICENSE](LICENSE).

---

**Powered by MrSuperOne**
