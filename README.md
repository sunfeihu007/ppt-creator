# PPT Creator · 内容规划大师

v3.0 · MIT · Python 3.10+

把演示材料规划成一条讲得清楚的论证链：**整套 PPT → 大块主体 → 小块内容 → 每页主旨 → 页内信息关系**。
保留引导式讨论、三轮合并确认与中断恢复，输出完整内容大纲和可以离线打开的互动 HTML 叙事地图。

本版聚焦内容规划。原有风格、配色、页面模板、视觉参考、生图后端和 PPTX 组装已移除；
待内容全部确认后，将内容交接给后续版面/版式设计。旧实现保留在 Git 历史中。

## 规划什么

- 整套目标、受众、核心主张、重点、叙事顺序与听众应记住的内容。
- 每个大块、小块的主题、主旨、重点、优先级及在整套和所属层级中的作用。
- 大块和小块之间的递进、因果、并列、对比、支撑、依赖、组成和归纳关系，以及关系成立的理由。
- 每页主题、一句话主旨、要点、听众问题、全篇作用、所属小块作用、证据、时长、讲述提示和页间衔接。
- 供后续信息图使用的信息实体、语义关系、阅读顺序和比较维度。此阶段不规定图形布局。

## 三轮工作流

| 阶段 | 合并确认内容 |
|:--|:--|
| 大纲讨论 | 整套目标、核心主张、大块划分、各块重点与关系 |
| 内容方向 | 各大块的小块内容、论证要点、主次、角色与关系 |
| 逐页规划 | 每页内容与作用、页内信息结构、衔接；预览大纲和 HTML 后整套确认 |

用户可以先要完整草稿，也可以随时回改；工具不会把保存草稿当作批准。
确认记录绑定内容指纹，改页通常仅使第三轮确认过期，改小块影响第二和第三轮，改全篇目标影响全部。

## 安装与使用

```bash
git clone https://github.com/sunfeihu007/ppt-creator.git
cd ppt-creator
python3 --version  # 3.10+，运行仅需标准库，无第三方依赖或 API key
```

将仓库放入宿主支持的 skills 目录，或让 Agent 阅读仓库中的 `SKILL.md`。
例如 Codex 使用项目 `.agents/skills/ppt-creator/`，Claude Code 使用 `.claude/skills/ppt-creator/`；
其他宿主使用其 Agent Skills 配置入口。

对 Agent 说：

> 帮我规划一份面向管理层的15分钟汇报。先讨论大块和逻辑，再细化到每一页，最后给我大纲和互动叙事地图。

Agent 按 [SKILL.md](SKILL.md) 与 [规划流程](references/planning-workflow.md) 分阶段推进。
无需先选择视觉风格，不需要生图服务。

## 直接试用互动总览

可直接下载并打开 [叙事地图示例](examples/output/content_map.html)，同时查看 [内容大纲示例](examples/output/content_outline.md)。

仓库提供一份**虚构的协作试点讨论示例**，它演示规划结构，不代表已确认的用户项目或真实业务成效。

```bash
python3 scripts/plan_tool.py --workspace /tmp/ppt-content-demo init --file examples/content-plan.json
python3 scripts/plan_tool.py --workspace /tmp/ppt-content-demo lint
python3 scripts/plan_tool.py --workspace /tmp/ppt-content-demo export --draft
```

用浏览器打开 `/tmp/ppt-content-demo/output/content_map.html`，无需服务器或网络：

- 默认展示大块推进、小块论证与页面归属的叙事主线；可切换层级关系图或按实际讲述顺序排列的逐页故事线；
- 层级树展开/收起，搜索标题、主旨、重点和页面编号；
- 点击节点看主旨、重点、作用与相关节点；实线表示归属，虚线表示选中节点的逻辑关系；
- 缩放/滚动浏览，逐页前后导航，通过 `#P03` 等锚点直接打开详情；
- 页内实体、关系、依据、讲述提示和衔接集中呈现。

HTML 的界面配色仅服务于内容浏览，不是未来 PPT 的风格。页面交互不直接修改计划或批准内容。

## 计划命令

默认工作目录 `./ppt_workspace`，也可用 `PPTC_WORKSPACE` 或 `--workspace` 指定。

```bash
python3 scripts/plan_tool.py init --file draft_plan.json
python3 scripts/plan_tool.py status
python3 scripts/plan_tool.py lint --stage outline
# 仅在真实用户确认后记录，不要为运行示例而自动批准
python3 scripts/plan_tool.py confirm --stage outline --note '用户确认的原话或准确摘要'
python3 scripts/plan_tool.py update --file content_patch.json
python3 scripts/plan_tool.py lint --stage content
python3 scripts/plan_tool.py confirm --stage content --note '用户确认依据'
python3 scripts/plan_tool.py update --file pages_patch.json
python3 scripts/plan_tool.py export --draft
python3 scripts/plan_tool.py confirm --stage pages --note '用户确认逐页内容的依据'
python3 scripts/plan_tool.py export
python3 scripts/plan_tool.py check-export
```

`update` 递归合并对象，**数组整体替换**；改一页可用 `page --id P03 --patch page_patch.json`。
`sync` 报告哪些确认已过期。未完成确认、有阻塞问题或校验 errors 时不能正式导出。
草稿始终可以导出供讨论，并明确标注未完成状态。机器校验不能代替论证质量和证据真实性的人工复核。

## 交付物

| 文件 | 内容 |
|:--|:--|
| `content_outline.md` | 整体叙事、层级内容、主旨/重点/作用/关系、逐页详纲、证据与设计交接 |
| `content_map.html` | 单文件离线互动总览、节点详情与逐页浏览 |
| `content_plan.json` | 同源机器可读的内容计划，供后续设计接手 |
| `content_manifest.json` | 计划版本、确认版本与交付文件校验值，可检测过期导出 |

正式交付表示内容已确认，可以进入下一个版面和版式设计阶段；本版不会继续执行视觉设计或生成幻灯片。

## 开发与验证

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖层级/关系完整性、阶段 Gate、确认失效、事实来源、草稿/正式导出、HTML 数据转义和 CLI 流程。
浏览器交互检查见 `tests/browser_smoke.py`（可选开发依赖 Playwright 和 Chromium）。
安装后运行 `python3 tests/browser_smoke.py`；使用系统浏览器时可设置 `PPTC_CHROMIUM=/usr/bin/chromium`。
检查把导出的完整单文件载入浏览器，覆盖离线内容、三个视图、导航、手机布局、输入转义和60页长稿。
运行时无第三方依赖；`requirements.txt` 留作兼容安装入口。

内容字段见 [内容模型](references/content-model.md)，事实约束见 [项目事实契约](references/project-contract.md)。
v3 不会原地覆盖 v2 的计划，迁移时保留原件，在新 workspace 重新整理内容层级并记录真实确认。
