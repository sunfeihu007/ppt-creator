# Phase 4：设计确定（配色 × 风格 × 后端）

前置：Read `references/design/INDEX.md`。

## 流程（两问一识别）

1. **问配色**：展示 palettes 表。用户有公司/品牌配色 → 优先使用；
   未指定 → 默认 INDEX.md 标注的默认配色。用户要自定义颜色 → 复制最接近的配色文件，
   仅改 Token 色值与描述词，存为新配色（如 custom-blue.md）。
2. **问风格**：展示 styles 表 + 兼容矩阵。以 `compatibility.json` 检查组合；blocked 组合必须
   拒绝并展示其中的原因与替代建议，禁止因用户坚持而静默放行。
   给出场景化建议（高层汇报→flat-editorial；复杂架构→glass-3d；对外交流→card-modern）。
3. **识别宿主原生能力并预检**（按 SKILL.md 路由）：
   - 当前 agent 有 AGY `generate_image` → AGY 原生；
   - 否则当前 agent 有 Codex `image_gen` → Codex 原生；
   - 否则检查 Gemini API key；
   - CLI 兼容桥仅在用户明确指定时检查，AGY 桥必须先通过 `agy -p` preflight。
   把将使用的 provider/transport/model 告知用户。不可仅因系统安装了某个 CLI 就覆盖宿主原生能力。
4. **在第一张样张前写入并锁定状态**：

```bash
# AGY CLI 宿主
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider agy --transport native

# Codex 宿主
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider codex --transport native

# 其他客户端 + Gemini API key
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider gemini --transport api

python scripts/plan_tool.py phase --name 4_design --status done
```

写入后不得对单页临时换后端或换模型。确需整体切换时，先运行
`plan_tool.py provider --name ... --transport ...`，并把已生成页面退回 `pending` 后统一重做。

## 修改配色的规则

用户中途要求换色（"红色改蓝色"）：只换 palette，style 不动；已生成页面状态退回 pending
全部重新生成（不同配色页面不能混在一套PPT里）。

## 新增配色/风格的规则

新增定义后必须为其与另一维的所有组合逐一登记 recommended/allowed/blocked，并运行
`python scripts/validate_design.py`。验证失败时不得写入 plan.json 或开始生图。

## 垫图规则

生图时附所选 style 目录下的 ref-*.jpg，提示词已由 make_prompt.py 自动声明
"参考图仅参考版式与质感，忽略其颜色"。配色准确性靠文字描述段保证。

AGY 原生 `generate_image` 当前无独立参考图参数，因此不把 `ref-*.jpg` 伪装成工具参数；
依靠提示词中的完整风格描述、已确认样张与逐页 QA 保持一致。Gemini API 与 Codex 原生/CLI
仍可在能力允许时提交参考图。
