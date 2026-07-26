# 项目事实契约与同步机制

本文件用于客户方案、售前、案例、金融、合规、招投标、量化承诺或多轮修改的 PPT。
普通内部汇报只需使用 `standard` 默认值，不要为了填字段而制造来源或事实。

## 目录

1. 适用原则
2. 三种保障级别
3. 项目契约结构
4. 需求与声明规则
5. 来源和素材真实性
6. 页面精确复用
7. 变更与自动失效
8. 生图前和生图后校验
9. 最终同步与交付物
10. 旧计划兼容

## 1. 适用原则

- 只记录用户明确决策、可靠材料、批准表述和必须遵守的边界。
- 不把行业名称、模型推测或 Agent 自己的常识写成项目事实。
- 项目契约使用通用字段；港口、金融、制造等具体词只属于项目数据。
- `plan.json` 保存当前有效状态，不保存无限增长的聊天记录或操作日志。
- 任何 API key、登录信息和凭据都不得进入 plan、来源、报告或交付清单。
- 当前 `delivery_mode` 只支持 `raster_slide`：整页图片嵌入 PPTX，演讲备注可编辑；
  不得把它描述为原生可编辑 PPT。

## 2. 三种保障级别

| `assurance_profile` | 适用情况 | 来源和案例规则 |
|:--|:--|:--|
| `standard` | 普通内部汇报、培训、创意型内容 | 有契约就执行；来源可选 |
| `client-facing` | 客户方案、售前、产品介绍 | 案例页缺少证据类型时警告 |
| `evidence-sensitive` | 真实案例、金融、合规、招投标、量化承诺 | 案例必须声明证据类型；实证必须引用来源；概念示意必须显示标签 |

Phase 1 在已有需求确认中一并记录该等级，不新增单独确认。用户未说明且不涉及外部事实时，
默认 `standard`。

## 3. 项目契约结构

新计划使用：

```json
{
  "schema_version": "2.4",
  "assurance_profile": "client-facing",
  "delivery_mode": "raster_slide",
  "requirements": [],
  "claim_constraints": [],
  "source_registry": [],
  "pages": []
}
```

完整页面可增加：

```json
{
  "id": "P08",
  "title": "客户案例",
  "requirement_refs": ["REQ-NAME-001"],
  "claim_refs": ["CLAIM-001"],
  "source_refs": ["SRC-001"],
  "evidence_level": "verified",
  "provenance_label": "",
  "asset_provenance": [
    {"asset": "site_photo", "type": "user_supplied"}
  ],
  "reused_from": null,
  "reuse_mode": null
}
```

脚本维护的 `dirty_reasons`、`prompt_input_hash` 和 `image_input_hash` 不得手工伪造。

## 4. 需求与声明规则

需求规则用于正式名称、必需内容和用户决策：

```json
{
  "id": "REQ-NAME-001",
  "decision": "平台名称统一使用正式批准名称",
  "required_terms": ["Nova Platform"],
  "forbidden_terms": ["Nove Platform"],
  "affected_pages": ["P01", "P05", "P30"]
}
```

声明规则用于能力边界、责任、审批、量化效果和禁止承诺：

```json
{
  "id": "CLAIM-001",
  "rule": "不得把建议方案表述为已落地成果",
  "forbidden_terms": ["已全面落地", "已验证达到"],
  "affected_pages": ["P08", "P09"]
}
```

规则没有 `affected_pages` 时视为全局规则。也可以在页面的 `requirement_refs` 或
`claim_refs` 中显式引用。必需词和禁止词使用精确字符串检查；不要依赖 Agent 每次重新理解。

更新项目契约：

```bash
python scripts/plan_tool.py contract --file contract.json
python scripts/plan_tool.py lint --ids all
```

`contract.json` 只允许包含 `assurance_profile`、`delivery_mode`、`requirements`、
`claim_constraints` 和 `source_registry`。

## 5. 来源和素材真实性

来源登记为全局注册表，页面只保存引用 ID：

```json
{
  "source_registry": [
    {
      "id": "SRC-001",
      "type": "file",
      "label": "客户提供的正式方案材料",
      "path": "materials/approved-proposal.pdf"
    },
    {
      "id": "SRC-002",
      "type": "user_statement",
      "label": "本轮对话确认的能力边界"
    }
  ]
}
```

- `verified`：真实案例、真实截图或可核验结论；必须有 `source_refs`。
- `anonymized`：来源真实但对客户名称、数据或界面做了脱敏。
- `conceptual`：方案设想、AI 生成示意或通用效果图；事实敏感型案例页必须提供
  `provenance_label`，例如“方案示意”。
- `general`：通用背景和说明性素材，不作为客户实证。

提示词只得到规则和可见标签，不暴露来源文件路径。最终清单只记录引用和产物，不复制源文档内容。

## 6. 页面精确复用

导航页、章节地图、免责声明等画面必须完全相同时，不要重新生图：

```bash
python scripts/plan_tool.py reuse --id P12 --from P02
```

等价 plan 字段：

```json
{
  "id": "P12",
  "reused_from": "P02",
  "reuse_mode": "exact_asset"
}
```

规则：

- 只支持 `exact_asset`，不支持“相似版式”复用。
- 复用页不生成独立 prompt 和图片。
- 组装和页面校验解析到源图片，但复用页可保留自己的演讲备注。
- 禁止引用不存在页面、自身引用或循环引用。
- 源页面变更时，所有复用后代自动失效。

## 7. 变更与自动失效

修改契约或页面内容后运行：

```bash
python scripts/plan_tool.py sync
python scripts/plan_tool.py status
```

页面内容推荐通过 patch 更新：

```json
{
  "title": "更新后的正式标题",
  "points": ["要点一", "要点二"],
  "source_refs": ["SRC-001"]
}
```

```bash
python scripts/plan_tool.py page --id P08 --patch page-patch.json
```

脚本按以下输入计算稳定 SHA-256：

- 页面标题、副标题、要点、布局提示和页面类型；
- 页面适用的需求、声明、来源和素材真实性；
- palette、style、industry、provider、transport 和 model；
- 精确复用源页面的输入哈希。

不使用文件修改时间。输入变化时只把受影响页面退回 `pending`，记录原因并清除旧哈希；
没有依赖关系的页面保持原状态。

## 8. 生图前和生图后校验

生图前必须运行：

```bash
python scripts/plan_tool.py lint --ids all
```

`make_prompt.py` 会再次检查目标页，发现必需词缺失、禁止词命中或证据规则错误时拒绝生成 prompt。

宿主具有视觉/OCR 能力时，把识别文本保存为：

```text
ppt_workspace/qa/ocr/P01.txt
ppt_workspace/qa/ocr/P02.txt
```

然后运行：

```bash
python scripts/verify_semantics.py
python scripts/verify_semantics.py --strict
```

默认行为：

- OCR 命中禁止词：错误；
- 标题或必需词未识别：警告；
- 缺少 OCR 文件：跳过；
- 报告写入 `ppt_workspace/qa/semantic-report.json`。

`--strict` 将标题和必需词缺失升级为错误；只有项目明确要求每页 OCR 时才加
`--require-ocr`。OCR 可能误识别中文，因此不得在普通项目中把低置信度差异全部硬阻断。

## 9. 最终同步与交付物

Phase 7 依次运行：

```bash
python scripts/plan_tool.py sync
python scripts/verify_pages.py
python scripts/plan_tool.py lint --ids all
python scripts/verify_semantics.py       # 有 OCR 时
python scripts/plan_tool.py sync-check
python scripts/build_ppt.py
```

`build_ppt.py` 再次执行语义和同步 gate，并自动生成：

```text
ppt_workspace/final_outline.md
ppt_workspace/output/<topic>.pptx
ppt_workspace/output/artifact_manifest.json
```

`final_outline.md` 是从 plan 自动导出的只读视图，不再手工双向维护。交付清单记录实际 PPTX、
页数、备注数量、解析后的源图片、像素尺寸、媒体编码和 SHA-256。

## 10. 旧计划兼容

- 没有 v2.4 字段的计划自动使用 `standard` 和 `raster_slide`。
- 已经进入 `prompted/generated/approved` 的旧页面，在首次读取时采用当前内容为哈希基线，
  不会仅因升级而全部失效。
- 旧 `template`、`page_type`、`industry` 和生图后端迁移规则继续有效。
- 未识别的自定义字段原样保留。
- v2.4 不实现 `editable_native` 或 `hybrid`；需要可编辑 PPT 时必须明确说明当前版本不支持，
  不得仅修改 `delivery_mode` 欺骗 gate。
