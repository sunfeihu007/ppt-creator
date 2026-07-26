# 风格：2.5D 插画（illust-2.5d）——颜色无关

> 来源方向：等距系统说明、产品旅程与业务场景叙事。等距2.5D插画＋克制几何线描，
> 适合平台介绍和偏叙事的技术汇报。

## 风格提示词骨架

```
Create a professional 16:9 presentation slide in a restrained 2.5D isometric-illustration
family. [COLOR_SCHEME]
Use a stable grid, one coherent isometric angle, simplified geometric objects, soft but
limited depth, consistent thin-line icons and generous negative space. Keep text and
diagram labels flat and crisp. Use illustration only where it clarifies a system or scene.
Avoid cartoon characters, mixed perspectives, excessive rounded cards, decorative emoji,
photorealistic/glass material mixing and crowded floating objects.
```

> v2.5 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **背景纹样**：封面铺细线几何放射纹样（圆弧网格、六边形，{SECONDARY}线条），内容页浅底
- **2.5D等距插画**：分层平台与用户内容直接相关的对象；不默认生成服务器、盾牌、芯片或机器人
- **图标**：细线描，{PRIMARY}或深灰单色；卡片内图标带{PRIMARY}淡描边方框
- **旅程结构**：沿一条等距路径组织大小不同的节点，文字保持扁平
- **装饰**：角落几何符号，克制使用

## 布局规范

- 中低密度，留白充足
- 骨架：等距旅程路径、左右对分（插画侧+文字侧）、2.5D分层塔＋左侧标签
- 标题行："{PRIMARY}引导词+{TITLE}主标题"结构

## 页面类型模板（旧版兼容）

### 封面页
```
Create a warm PPT cover slide, 16:9, 2.5D isometric illustration style. [COLOR_SCHEME]
标题：[主题]（{TITLE}超大粗体）+细体副标题。背景铺细线几何放射纹样（{SECONDARY}线条），
{PRIMARY}小色块和箭头点缀节点。扁平+线描，对称大气。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 架构页（2.5D分层）
```
Create a PPT architecture slide, 16:9, 2.5D isometric illustration. [COLOR_SCHEME]
中央2.5D等距分层平台：普通层中性色带厚度，核心层{PRIMARY}发光高亮；左侧每层文字标签，
层间细引导线。柔和光效阴影，插画统一单色系。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 流程页（等距旅程）
```
Create a PPT content slide, 16:9, line illustration style. [COLOR_SCHEME]
标题：[标题]（{TITLE}粗体，可带{PRIMARY}引导词）。沿一条等距路径放置按重要性变化的节点，
用统一箭头连接；一个主节点配大插画，其余节点用小型几何和扁平文字，不建立等宽卡片列。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（2.5D分层）、ref-03（等距旅程）
