# 配色：橙青绿（orange-teal）★公司默认配色

> 来源：公司现行 PPT 实测取色。品牌双色 = 活力橙 + 深青绿。

## 色值定义（Token 表）

| Token | 色值 | 自然语言描述词（写入提示词用） | 用途 |
|:---|:---|:---|:---|
| `{PRIMARY}` | `#E87818` | 活力橙 / warm vivid orange | 重点强调、序号、数据流、关键卡片头 |
| `{SECONDARY}` | `#00655F` | 深青绿 / deep teal green | 结构元素、图标、标题引导块、次级卡片 |
| `{ACCENT}` | `#66B94A` | 亮绿 / fresh green | 成功态、小点缀（克制使用） |
| `{BG}` | `#FFFFFF` → `#F6F9F8` | 白到极浅灰绿渐变 | 背景 |
| `{TITLE}` | `#333333` | 深灰 | 标题文字 |
| `{BODY}` | `#666666` | 中灰 | 正文文字 |
| `{OK}` | `#66B94A` | 绿 | 正确/完成 |
| `{WARN}` | `#E87818` | 橙 | 警示（与主色同源） |

## v2.3 视觉角色 Token

| Token | 色值 | 自然语言描述词 | 用途 |
|:---|:---|:---|:---|
| `{BACKGROUND}` | `#FFFFFF` → `#F6F9F8` | 白到极浅灰绿 | 主背景 |
| `{SURFACE}` | `#FFFFFF` | 白色 | 卡片与信息表面 |
| `{STRUCTURE}` | `#00655F` | 深青绿 | 网格、框架、主结构、图标 |
| `{FOCUS}` | `#E87818` | 活力橙 | 唯一聚焦点，严格约 3% |
| `{TEXT_PRIMARY}` | `#333333` | 深灰 | 标题与主要文字 |
| `{TEXT_SECONDARY}` | `#666666` | 中灰 | 正文与说明 |
| `{BORDER}` | `#C9DDD9` | 浅灰青 | 细线与边界 |
| `{INVERSE_BACKGROUND}` | `#00524D` | 深青绿 | 章节页与反白页 |
| `{INVERSE_TEXT}` | `#FFFFFF` | 白色 | 深底文字 |
| `{STATUS_OK}` | `#4B8F3A` | 状态绿 | 明确成功状态 |
| `{STATUS_WARN}` | `#B85B13` | 深橙 | 明确警告状态 |
| `{STATUS_RISK}` | `#A33B2B` | 砖红 | 明确风险状态 |

## 双色使用规则（重要）

- **85-12-3**：中性色（白/灰）约85%，青绿约12%（承担"结构"），橙严格限制在约3%（只做微小强调）；
- 禁止橙绿 50/50 平分画面——橙是聚光灯，绿是骨架；
- 禁止橙色大色块；橙只用于小型发光点、关键标记、序号或微型激活态；
- 橙绿相邻时用白色/留白隔开，不直接接触大面积拼色；
- 图标统一青绿单色系，橙只出现在需要视线聚焦的一个点上。

## 提示词配色描述段（脚本拼装用）

```
Color scheme: white background, deep teal green (#00655F) as structural color for
icons/frames/section blocks, warm vivid orange (#E87818) ONLY for tiny highlights.
Color distribution: 85% clean white/neutral negative space, 12% deep teal structural
elements, and STRICTLY 3% orange for small glowing dots, critical markers, numbers, or
micro active states. NEVER balance orange and teal evenly. NEVER use orange for large
blocks. Neutral gray text. No other hues.
```
