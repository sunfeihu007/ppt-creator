# 配色：瓷白晴蓝（porcelain-azure）

> 温润瓷白承担空间，石墨负责结构，只保留一处克制晴蓝聚焦。用于产品、AI、金融科技和
> 高端客户方案中的明亮表达；区别于冷灰工程感的 `graphite-cobalt`。

## 兼容旧模板 Token

| Token | 色值 | 名称 | 用途 |
|:---|:---|:---|:---|
| `{PRIMARY}` | `#27313B` | 石墨 | 标题、结构与框架 |
| `{SECONDARY}` | `#1D6FD1` | 晴蓝 | 单一聚焦与关键节点 |
| `{ACCENT}` | `#1D6FD1` | 晴蓝 | 同上 |
| `{BG}` | `#F6F4F0` → `#FFFFFF` | 瓷白 | 背景明度层级 |
| `{TITLE}` | `#1A232B` | 深石墨 | 标题 |
| `{BODY}` | `#59646E` | 中性灰 | 正文 |
| `{OK}` | `#2F7254` | 状态绿 | 正确/完成 |
| `{WARN}` | `#865D18` | 深琥珀 | 警示 |

## v2.6 视觉角色 Token

| Token | 色值 | 名称 | 用途 |
|:---|:---|:---|:---|
| `{BACKGROUND}` | `#F6F4F0` → `#FFFFFF` | 温润瓷白 | 主背景 |
| `{SURFACE}` | `#FFFFFF` | 白色 | 内容、证据和实色文字承载面 |
| `{STRUCTURE}` | `#27313B` | 石墨 | 标题、框架、网格和普通节点 |
| `{FOCUS}` | `#1D6FD1` | 晴蓝 | 一页唯一聚焦对象 |
| `{FOCUS_TEXT}` | `#1558A6` | 深晴蓝 | 浅底上的聚焦文字 |
| `{TEXT_PRIMARY}` | `#1A232B` | 深石墨 | 标题与主要文字 |
| `{TEXT_SECONDARY}` | `#59646E` | 中性灰 | 正文与说明 |
| `{BORDER}` | `#D8D5CF` | 暖浅灰 | 分隔线与边界 |
| `{INVERSE_BACKGROUND}` | `#1C2731` | 深石墨蓝 | 章节页与反白页 |
| `{INVERSE_TEXT}` | `#F8FAFC` | 冷白 | 深底文字 |
| `{STATUS_OK}` | `#2F7254` | 状态绿 | 状态填充、图标和边界 |
| `{STATUS_OK_TEXT}` | `#245C43` | 深状态绿 | 浅底上的成功文字 |
| `{STATUS_WARN}` | `#865D18` | 深琥珀 | 状态填充、图标和边界 |
| `{STATUS_WARN_TEXT}` | `#6E4A10` | 深琥珀棕 | 浅底上的警告文字 |
| `{STATUS_RISK}` | `#9C3F3F` | 深红 | 状态填充、图标和边界 |
| `{STATUS_RISK_TEXT}` | `#7C3030` | 深风险红 | 浅底上的风险文字 |

## 使用规则

- 瓷白、白色和石墨占 90% 以上；晴蓝只承担一个决定性聚焦对象。
- 背景的温度来自暖中性灰，不使用奶油黄、玫瑰金或紫蓝渐变制造“高级感”。
- 玻璃风格只允许一个主要磨砂层；文字、表格和密集架构节点使用实色或高不透明表面。
- 适合产品、AI、金融科技和客户方案；工程高密图优先 `graphite-cobalt` 或行业色板。
- `FOCUS`、`STATUS_*` 用于填充、线条和图标；小字使用对应的 `*_TEXT`。

## 提示词配色描述段

```
Use a warm porcelain neutral palette: background {BACKGROUND}, solid content surfaces
{SURFACE}, graphite structure {STRUCTURE}, primary text {TEXT_PRIMARY}, secondary text
{TEXT_SECONDARY}, and warm-gray borders {BORDER}. Use restrained azure focus {FOCUS}
for at most one decisive object; when focus appears as small text use {FOCUS_TEXT}.
Keep text, tables, and dense diagram nodes on solid or near-opaque surfaces. Use status
colors only for real semantics with readable *_TEXT roles. For inverse pages use
{INVERSE_BACKGROUND} with {INVERSE_TEXT}. No purple-blue gradient, rose gold, milky
yellow wash, multicolor technology accents, or decorative all-over glass.
```
