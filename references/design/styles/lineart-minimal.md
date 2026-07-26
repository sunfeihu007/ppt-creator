# 风格：极简线描（lineart-minimal）——颜色无关

> 来源方向：机构型极简说明、单一论点与单色技术线描。极浅底＋细线插画＋大留白，知性安静。
> 单色倾向最强的风格：主要只用 {PRIMARY} 一个色 + 语义色，双色配色中 {SECONDARY} 用量极少。

## 风格提示词骨架

```
Create a professional 16:9 presentation slide in an ultra-minimal monochrome line-art
family. [COLOR_SCHEME]
Use a strict quiet grid, very large negative space, uniform thin strokes, sparse geometric
corner marks and one coherent outline-icon/illustration language. Keep the composition
nearly monochrome: structure and text carry the page, while the focal color appears in no
more than one or two tiny elements. No 3D, no gradient, no glow, no shadow, no filled icon
set, no decorative card wall and no mixed line weights.
```

> v2.6 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **细线描插画**：单线条勾勒场景与实物，线宽一致，无填充或极淡填充，线色为浅灰蓝或{SECONDARY}淡化
- **几何角标**：页角细线三角/斜线网格，极淡
- **语义标注**：{WARN}叉/删除线=错误项，{OK}勾=正确项，仅用于对比场景
- **页脚签名**：全篇统一小字页脚，建立系列感
- **无3D、无渐变、无发光**
- **近乎单色**：线稿只用所选配色的主深色/冷色；明亮辅色全页最多用于1–2个微小点或微型元素

## 布局规范

- 低密度，每页一个核心论点
- 骨架：左右两世界对比、一个主线描＋窄注释栏、细线框表格
- 结论行：页底箭头符号+一句话结论（{PRIMARY}粗体）

## 页面类型模板（旧版兼容）

所有模板必须遵守：Monochrome Line Rule — keep line art almost entirely monochrome
using the palette's primary dark/cool color. A bright secondary accent may appear in no
more than ONE or TWO tiny dots or micro-elements in the entire composition. Keep the
result ultra-minimal and visually silent.

### 封面页
```
Create a minimal PPT cover slide, 16:9, thin line-art illustration style, NO 3D, NO gradient.
[COLOR_SCHEME]
左侧：细线描插画组合（[主题相关实物]，单色细线条等宽）；页角细线几何装饰。
右侧：{PRIMARY}特大粗体标题[主题]+{BODY}细体副标题。大量留白，安静克制；不补日期。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 要点页（主线描＋注释）
```
Create a minimal PPT content slide, 16:9, line-art style. [COLOR_SCHEME]
标题：[标题]（{PRIMARY}粗体居左）。一个内容相关的主线描占主要面积，旁边用窄注释栏
列出提供的短语和说明；只在一处使用聚焦色，其余留白。不为每条文字配独立图标。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 对比/流程页
```
Create a minimal PPT slide, 16:9, line-art style. [COLOR_SCHEME]
标题：[标题]。布局：[左右对比/三步流程]，线描插画表现[场景]；正确项{OK}勾标注、
错误项{WARN}叉标注，其余单色。底部箭头+一句话结论（{PRIMARY}粗体）。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（主线描＋注释）、ref-03（流程）
