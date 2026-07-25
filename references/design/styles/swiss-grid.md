# 风格：瑞士网格（swiss-grid）——颜色无关

> 来源方向：瑞士国际主义、Neo-Swiss 大字报、机构型极简。适合科技产品、正式售前、
> 数据汇报和跨行业解决方案。颜色必须服从单一聚焦色原则。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in a Swiss international grid family.
[COLOR_SCHEME]
Use a rigorous 12-column grid, strong typographic scale contrast, left alignment,
asymmetric negative space, square geometry, calibrated gray surfaces and 1px hairline
rules. Use one saturated focal color only. Interpret any palette background gradient as
a flat dominant field for this style. Use no 3D, no glow, no visible gradient, no shadow,
no decorative transparency, no rounded accent pill and no multicolor icon set. All page
types must feel like one institutional graphic system.
```

## 视觉语法

- **网格**：12 栏；主要元素吸附统一基线，非对称但不失衡。
- **字体**：全程无衬线；大标题细字重，小标签中高字重。
- **几何**：直角、纯色、发丝线；不使用圆角悬浮卡。
- **颜色**：中性色占主导，一页只允许一个聚焦色。
- **图片**：直角裁切、无阴影；图片说明贴齐网格。
- **图标**：统一线性图标或几何符号，不为每条文字配图标。
- **图表**：单色阶梯，其余系列灰化；标签直接靠近数据。
- **签名元素**：章节编号、小方块、发丝线和超大数字。

## 页面类型模板（旧版 make_prompt.py 兼容）

### 封面页
```
Create a Swiss-grid PPT cover, 16:9. [COLOR_SCHEME]
超大无衬线标题吸附12栏网格，单一纯色矩形作为视觉锚点，大量非对称留白，直角、无阴影、无渐变。
```

### 架构图页
```
Create a Swiss-grid architecture slide, 16:9. [COLOR_SCHEME]
使用12栏网格、直角扁平模块、1px发丝连接线和单一聚焦节点；标签完整、层级清晰、无3D。
```

### 详解页
```
Create a Swiss-grid detail slide, 16:9. [COLOR_SCHEME]
非对称3:7或4:8图文网格，标题与正文左对齐，使用纯色结构块和发丝分割线，避免等宽卡片墙。
```

## 使用边界

- 不与多色高亮、强渐变、玻璃光效、厚阴影组合。
- 章节页可以使用同色板深底反白，但网格、字体和锚点色不变。
- 高密度页面优先增加网格秩序，不通过缩小文字或增加容器解决。
