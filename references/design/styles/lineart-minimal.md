# 风格：极简线描（lineart-minimal）——颜色无关

> 版式来源：智能理货审核系统立项汇报。极浅底+单色细线描插画+大留白，知性安静。
> 单色倾向最强的风格：主要只用 {PRIMARY} 一个色 + 语义色，双色配色中 {SECONDARY} 用量极少。

## 视觉元素

- **细线描插画**：单线条勾勒场景与实物，线宽一致，无填充或极淡填充，线色为浅灰蓝或{SECONDARY}淡化
- **几何角标**：页角细线三角/斜线网格，极淡
- **语义标注**：{WARN}叉/删除线=错误项，{OK}勾=正确项，仅用于对比场景
- **页脚签名**：全篇统一小字页脚，建立系列感
- **无3D、无渐变、无发光**

## 布局规范

- 低密度，每页一个核心论点
- 骨架：左右两世界对比、三要素横排（大图标+粗体短语+两行说明）、细线框表格
- 结论行：页底箭头符号+一句话结论（{PRIMARY}粗体）

## 页面类型模板

### 封面页
```
Create a minimal PPT cover slide, 16:9, thin line-art illustration style, NO 3D, NO gradient.
[COLOR_SCHEME]
左侧：细线描插画组合（[主题相关实物]，单色细线条等宽）；页角细线几何装饰。
右侧：{PRIMARY}特大粗体标题[主题]+{BODY}细体副标题与日期。大量留白，安静克制。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 要点页（三要素横排）
```
Create a minimal PPT content slide, 16:9, line-art style. [COLOR_SCHEME]
标题：[标题]（{PRIMARY}粗体居左）。三组横排：大号细线描图标+{PRIMARY}粗体短语+
两行{BODY}说明。等距水平对齐，其余留白。页脚一行统一小字。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 对比/流程页
```
Create a minimal PPT slide, 16:9, line-art style. [COLOR_SCHEME]
标题：[标题]。布局：[左右对比/三步流程]，线描插画表现[场景]；正确项{OK}勾标注、
错误项{WARN}叉标注，其余单色。底部箭头+一句话结论（{PRIMARY}粗体）。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（三要素）、ref-03（流程）
