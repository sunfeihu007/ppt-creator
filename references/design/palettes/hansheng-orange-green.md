# 配色：翰声橙绿（hansheng-orange-green）★公司默认配色

> 来源：翰声智联络中心方案（公司现行 PPT 实测取色）。品牌双色 = 活力橙 + 深青绿。

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

## 双色使用规则（重要）

- **60-30-10**：中性色（白/灰）约60%，青绿约30%（承担"结构"），橙约10%（只做"强调"）；
- 禁止橙绿 50/50 平分画面——橙是聚光灯，绿是骨架；
- 橙绿相邻时用白色/留白隔开，不直接接触大面积拼色；
- 图标统一青绿单色系，橙只出现在需要视线聚焦的一个点上。

## 提示词配色描述段（脚本拼装用）

```
Color scheme: white background, deep teal green (#00655F) as structural color for
icons/frames/section blocks, warm vivid orange (#E87818) ONLY for key highlights,
numbers and emphasis. Neutral gray text. No other hues.
```

参考图：`ref-01.jpg`（封面）、`ref-02.jpg`（内容页）——仅供取色，版式不参考。
