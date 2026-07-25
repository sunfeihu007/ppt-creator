# Phase 4：设计确定（配色 × 风格 × 行业视觉修饰 × 后端）

前置：Read `references/design/INDEX.md`。

## 流程（三层视觉选择＋后端识别）

1. **确认品牌优先级**：先确认是否有客户 VI、Logo、字体、模板或指定品牌色；客户品牌优先，
   公司 `orange-teal` 次之，行业 palette 只在没有品牌限制时兜底。真实品牌资产不得被行业默认值覆盖。
2. **问配色**：展示 palettes 表。用户要自定义颜色 → 复制最接近的配色文件，
   同时修改旧 Token、全部 v2.3 语义 Token、使用规则和描述段，存为新配色（如 custom-blue.md）。
   不得只换主色而保留冲突的聚焦色、状态色或深底色。
3. **问风格**：展示 styles 表 + 兼容矩阵。以 `compatibility.json` 检查组合；blocked 组合必须
   拒绝并展示其中的原因与替代建议，禁止因用户坚持而静默放行。
   优先按视觉职责建议：正式网格→`swiss-grid`；工程/架构密集→`industrial-diagram`；
   证据/案例/高层汇报→`flat-editorial`；只有确实需要时才使用玻璃或 HUD。
4. **选择行业视觉修饰**：从 `general/port-terminal/finance/automotive-manufacturing` 中选择，
   只控制几何、图片处理、图标和视觉语气。它不得修改内容大纲，也不得强制覆盖品牌配色。
   未指定时使用 `general`。
5. **识别宿主原生能力并预检**（按 SKILL.md 路由）：
   - 当前 agent 有 AGY `generate_image` → AGY 原生；
   - 否则当前 agent 有 Codex `image_gen` → Codex 原生；
   - 否则检查 Gemini API key；
   - CLI 兼容桥仅在用户明确指定时检查，AGY 桥必须先通过 `agy -p` preflight。
   把将使用的 provider/transport/model 告知用户。不可仅因系统安装了某个 CLI 就覆盖宿主原生能力。
6. **在第一张样张前写入并锁定状态**：

```bash
# AGY CLI 宿主
python scripts/plan_tool.py design --palette orange-teal --style industrial-diagram \
  --industry port-terminal --provider agy --transport native

# Codex 宿主
python scripts/plan_tool.py design --palette finance-navy-teal --style flat-editorial \
  --industry finance --provider codex --transport native

# 其他客户端 + Gemini API key
python scripts/plan_tool.py design --palette industrial-navy-orange --style industrial-diagram \
  --industry automotive-manufacturing --provider gemini --transport api

python scripts/plan_tool.py phase --name 4_design --status done
```

写入后不得对单页临时换后端或换模型。确需整体切换时，先运行
`plan_tool.py provider --name ... --transport ...`，并把已生成页面退回 `pending` 后统一重做。

## 修改视觉锁的规则

用户中途要求换色（"红色改蓝色"）：只换 palette，style 不动；已生成页面状态退回 pending
全部重新生成（不同配色页面不能混在一套PPT里）。

用户中途要求换风格或行业视觉修饰：整套重新锁定，所有已生成页面退回 `pending`。页面之间需要
变化时优先调整 `page_type` 和 `layout_hint`，不得给单页临时切换 style 或 industry。

## 新增配色/风格的规则

新增 palette/style 后必须为其与另一维的所有组合逐一登记 recommended/allowed/blocked。
新增 page type/industry 后必须登记索引、Markdown 提示词片段和有效默认组合。统一运行
`python scripts/validate_design.py`；验证失败时不得写入 plan.json 或开始生图。

## 垫图规则

生图时附所选 style 目录下的 ref-*.jpg，提示词已由 make_prompt.py 自动声明
"参考图仅参考版式与质感，忽略其颜色"。配色准确性靠文字描述段保证。

某个 style 没有 `ref-*.jpg` 时，使用该风格的完整提示词骨架，不虚构参考图参数；设计样张
仍需覆盖风格家族、页面类型差异和行业视觉语气。

AGY 原生 `generate_image` 当前无独立参考图参数，因此不把 `ref-*.jpg` 伪装成工具参数；
依靠提示词中的完整风格描述、已确认样张与逐页 QA 保持一致。Gemini API 与 Codex 原生/CLI
仍可在能力允许时提交参考图。
