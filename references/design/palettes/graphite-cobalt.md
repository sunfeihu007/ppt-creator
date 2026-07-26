# 配色：石墨钴蓝（graphite-cobalt）

> 冷灰与石墨承担结构，只保留一处钴蓝聚焦。用于通用技术、AI、产品和解决方案汇报，
> 是新项目中替代传统浅蓝渐变科技模板的克制选择。

## 兼容旧模板 Token

| Token | 色值 | 名称 | 用途 |
|:---|:---|:---|:---|
| `{PRIMARY}` | `#202833` | 石墨 | 标题、结构与框架 |
| `{SECONDARY}` | `#2457C5` | 钴蓝 | 单一聚焦与关键节点 |
| `{ACCENT}` | `#2457C5` | 钴蓝 | 同上 |
| `{BG}` | `#F3F5F7` → `#FFFFFF` | 冷灰白 | 背景 |
| `{TITLE}` | `#17202A` | 深石墨 | 标题 |
| `{BODY}` | `#4C5968` | 蓝灰 | 正文 |
| `{OK}` | `#2F7D5C` | 状态绿 | 正确/完成 |
| `{WARN}` | `#8B621B` | 深琥珀 | 警示 |

## v2.5 视觉角色 Token

| Token | 色值 | 名称 | 用途 |
|:---|:---|:---|:---|
| `{BACKGROUND}` | `#F3F5F7` → `#FFFFFF` | 冷灰白 | 主背景 |
| `{SURFACE}` | `#FFFFFF` | 白色 | 信息与证据表面 |
| `{STRUCTURE}` | `#202833` | 石墨 | 标题、框架、网格和普通节点 |
| `{FOCUS}` | `#2457C5` | 钴蓝 | 一页唯一聚焦对象 |
| `{FOCUS_TEXT}` | `#17469D` | 深钴蓝 | 浅底上的聚焦文字 |
| `{TEXT_PRIMARY}` | `#17202A` | 深石墨 | 标题与主要文字 |
| `{TEXT_SECONDARY}` | `#4C5968` | 蓝灰 | 正文与说明 |
| `{BORDER}` | `#C9D1DB` | 冷灰 | 分隔线与边界 |
| `{INVERSE_BACKGROUND}` | `#202833` | 石墨 | 章节页与反白页 |
| `{INVERSE_TEXT}` | `#F7F9FC` | 冷白 | 深底文字 |
| `{STATUS_OK}` | `#2F7D5C` | 状态绿 | 状态填充、图标和边界 |
| `{STATUS_OK_TEXT}` | `#236147` | 深状态绿 | 浅底上的成功文字 |
| `{STATUS_WARN}` | `#8B621B` | 深琥珀 | 状态填充、图标和边界 |
| `{STATUS_WARN_TEXT}` | `#6F4B0F` | 深琥珀棕 | 浅底上的警告文字 |
| `{STATUS_RISK}` | `#A23C3C` | 深红 | 状态填充、图标和边界 |
| `{STATUS_RISK_TEXT}` | `#823030` | 深风险红 | 浅底上的风险文字 |

## 使用规则

- 冷灰/白与石墨占 90% 以上，钴蓝只承担决定性聚焦。
- 不使用紫蓝渐变、蓝色外发光或多组高饱和科技色。
- `FOCUS`、`STATUS_*` 主要用于色块、线条和图标；小字使用对应的 `*_TEXT`。
- 平面风格把背景解释为冷灰到白的层级变化，不画可见渐变。

## 提示词配色描述段

```
Use a cold neutral palette: background {BACKGROUND}, surfaces {SURFACE}, graphite
structure {STRUCTURE}, primary text {TEXT_PRIMARY}, secondary text {TEXT_SECONDARY},
and borders {BORDER}. Use cobalt focus {FOCUS} for at most one decisive object; when
focus appears as small text use {FOCUS_TEXT}. Use status fills only for real semantics,
with readable status text {STATUS_OK_TEXT}, {STATUS_WARN_TEXT}, or {STATUS_RISK_TEXT}.
For inverse pages use {INVERSE_BACKGROUND} with {INVERSE_TEXT}. No purple-blue gradient,
neon glow, or multicolor technology accents.
```
