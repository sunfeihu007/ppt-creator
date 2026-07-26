# 配色：工业藏青橙（industrial-navy-orange）

> 定位：汽车、制造、工业 AI 与部分港口方案。藏青和石墨灰承担工程结构，安全橙只作聚焦。

## 兼容旧模板 Token

| Token | 色值 | 自然语言描述词 | 用途 |
|:---|:---|:---|:---|
| `{PRIMARY}` | `#263746` | 工业藏青 | 框架、标题与设备结构 |
| `{SECONDARY}` | `#71808C` | 钢铁灰 | 次级结构与线描 |
| `{ACCENT}` | `#E56A18` | 安全橙 | 关键节点与小面积强调 |
| `{BG}` | `#F4F6F7` → `#FFFFFF` | 冷灰白 | 背景 |
| `{TITLE}` | `#1B242C` | 近黑蓝 | 标题 |
| `{BODY}` | `#5F6B75` | 钢灰 | 正文 |
| `{OK}` | `#3E7D57` | 状态绿 | 正确/完成 |
| `{WARN}` | `#B55312` | 深橙 | 警示 |

## v2.3 视觉角色 Token

| Token | 色值 | 自然语言描述词 | 用途 |
|:---|:---|:---|:---|
| `{BACKGROUND}` | `#F4F6F7` → `#FFFFFF` | 冷灰白 | 主背景 |
| `{SURFACE}` | `#FFFFFF` | 白色 | 模块与图表表面 |
| `{STRUCTURE}` | `#263746` | 工业藏青 | 工程网格、设备线条、主框架 |
| `{FOCUS}` | `#E56A18` | 安全橙 | 唯一关键聚焦点 |
| `{FOCUS_TEXT}` | `#984006` | 深安全橙 | 浅底上的聚焦文字 |
| `{TEXT_PRIMARY}` | `#1B242C` | 近黑蓝 | 标题与主要文字 |
| `{TEXT_SECONDARY}` | `#5F6B75` | 钢灰 | 正文与说明 |
| `{BORDER}` | `#C8D0D6` | 浅钢灰 | 分隔线与边界 |
| `{INVERSE_BACKGROUND}` | `#17242F` | 深石墨蓝 | 章节页与反白页 |
| `{INVERSE_TEXT}` | `#F7F9FA` | 冷白 | 深底文字 |
| `{STATUS_OK}` | `#3E7D57` | 状态绿 | 明确成功状态 |
| `{STATUS_OK_TEXT}` | `#2C6644` | 深状态绿 | 浅底上的成功文字 |
| `{STATUS_WARN}` | `#A94C10` | 深安全橙 | 明确警告状态 |
| `{STATUS_WARN_TEXT}` | `#7B3409` | 深警告橙 | 浅底上的警告文字 |
| `{STATUS_RISK}` | `#A33A31` | 深红 | 明确风险状态 |
| `{STATUS_RISK_TEXT}` | `#7E2A23` | 深风险红 | 浅底上的风险文字 |

## 使用规则

- 中性色和藏青合计至少 90%，安全橙通常不超过 5%。
- 安全橙不用于普通正文和大面积背景。
- 钢铁质感通过冷灰、线条和几何表达，不使用金属渐变。

## 提示词配色描述段

```
Color scheme: cold off-white and white surfaces, industrial navy (#263746) and graphite
gray for engineering structure, grids and equipment linework, safety orange (#E56A18)
ONLY for one critical node, active stage or small marker. Precise, modular and reliable.
No metallic gradients, no rainbow status coding and no oversized orange blocks.
```
