# Phase 4：设计确定（配色 × 风格 × 后端）

前置：Read `references/design/INDEX.md`。

## 流程（两问一探测）

1. **问配色**：展示 palettes 表。用户有公司/品牌 → 优先品牌配色（如翰声橙绿）；
   未指定 → 默认 INDEX.md 标注的默认配色。用户要自定义颜色 → 复制最接近的配色文件，
   仅改 Token 色值与描述词，存为新配色（如 custom-blue.md）。
2. **问风格**：展示 styles 表 + 兼容矩阵。检查所选组合合法（hud-frame 仅配深色配色）。
   给出场景化建议（高层汇报→flat-editorial；复杂架构→glass-3d；对外交流→card-modern）。
3. **探测生图后端**（按 SKILL.md 顺序），告知用户将使用哪个后端。
4. 写入状态：
```bash
python scripts/plan_tool.py design --palette hansheng-orange-green --style glass-3d --provider codex
python scripts/plan_tool.py phase --name 4_design --status done
```

## 修改配色的规则

用户中途要求换色（"红色改蓝色"）：只换 palette，style 不动；已生成页面状态退回 pending
全部重新生成（不同配色页面不能混在一套PPT里）。

## 垫图规则

生图时附所选 style 目录下的 ref-*.jpg，提示词已由 make_prompt.py 自动声明
"参考图仅参考版式与质感，忽略其颜色"。配色准确性靠文字描述段保证。
