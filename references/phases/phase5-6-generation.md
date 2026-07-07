# Phase 5–6：页面生成详细指令

## 通用循环（每页）

1. 与用户确认该页内容要点（核心观点/展示信息/呈现方式：列表、图表、对比、流程、图文）；
2. 更新 plan.json 中该页的 title/points/layout_hint；
3. `python scripts/make_prompt.py --page PXX` 生成提示词文件（禁止手写完整提示词；
   如页面有特殊需求，编辑 plan.json 的 layout_hint 后重新生成提示词）；
4. 生图：
   - Codex 环境：读取 prompts/PXX.txt 内容，用内置 image_gen 工具生成 1920×1080 图片，
     保存到 ppt_workspace/pages/PXX.png，然后 `plan_tool.py page --id PXX --status generated`；
   - 其他环境：`python scripts/gen_image.py --page PXX`（自动重试、自动裁切16:9、自动更新状态）；
5. **目检**：用视觉能力查看图片，对照 references/constraints.md 检查清单；
6. 展示给用户 → 通过则 `plan_tool.py page --id PXX --status approved`，继续下一页；
   不通过则调整后重新生成（最多3轮，仍失败与用户讨论换呈现方式）。

## Phase 5 框架页

先做封面 → 目录 → 各过渡页 → 总结/结束页。**先生成封面1页给用户确认整体风格**，
确认后才批量做其余框架页。全部 approved 后 `plan_tool.py phase --name 5_framework --status done`。

## Phase 6 内容页

按部分分批生成（每批2-4页），每批展示确认。注意：
- 每页提示词由脚本拼装，保证风格一致，杜绝后半程漂移；
- 重点页信息密度高，过渡页低；避免所有页密度均等；
- 目检特别注意：中文乱码、文字截断、图标是否单色系、与前序页风格是否一致。
全部 approved 后 `plan_tool.py phase --name 6_content_pages --status done`。
