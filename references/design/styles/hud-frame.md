# 风格：HUD 线框（hud-frame）——仅限深色配色

> 版式来源：宁波外理智能理货位置复核。⚠️ 只能搭配深色配色（如 deep-space），
> 且须用户明确接受深色背景。冲击力最强，适合创新立项、概念演示、评奖路演。

## 视觉元素

- **HUD线框**：{PRIMARY}细发光描边框、四角括号取景框、扫描线
- **3D线框实体**：主题实体（集装箱/建筑/设备）用{PRIMARY}发光线框+半透明面构建
- **数据标注**：等宽字体样式参数标签（[ ACCURACY: 99.9% ]式），中英混排小标
- **辉光**：主元素外发光；{PRIMARY}粒子、光束、景深
- **警示**：关键风险用{WARN}高亮
- **中英双语**：中文为主，关键术语附英文小字

## 布局规范

- 中高密度；深色下留白靠"暗区"实现
- 主视觉居中/居右，参数标注环绕；路线图=横向发光轴+节点光柱
- 小字与背景对比度必须足够（{TITLE}近白）

## 页面类型模板

### 封面页
```
Create a sci-fi HUD style PPT cover slide, 16:9. [COLOR_SCHEME]
标题：[主题]（{TITLE}粗体大字）+{BODY}细体副标题。
右侧3D发光线框场景（[主题实体]），HUD取景框与扫描元素，角落等宽字体参数标签，
{PRIMARY}粒子与光束。所有文字清晰可读。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

### 目录页
```
Create a sci-fi HUD style PPT contents slide, 16:9. [COLOR_SCHEME]
标题居中。[N]个发光描边圆角卡片两行排列：{SECONDARY}线框图标+{PRIMARY}序号+条目名+
一行小字说明；卡片间发光路径线串联。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

### 内容页
```
Create a sci-fi HUD style PPT slide, 16:9. [COLOR_SCHEME]
标题：[标题]（{TITLE}粗体，关键词{WARN}）。主视觉发光线框示意图（[描述]），
HUD标注框环绕列出要点（{PRIMARY}边框、等宽字体字段名）；风险用{WARN}高亮。
Layout reference: attached image (layout/texture only, IGNORE exact colors).
```

参考图：ref-01（封面）、ref-02（目录）、ref-03（内容）
