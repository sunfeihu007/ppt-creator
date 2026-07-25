# 风格：2.5D 插画（illust-2.5d）——颜色无关

> 版式来源：外一知识中台介绍。等距2.5D插画+几何线描装饰，温暖亲和，
> 适合知识中台、数据平台介绍、偏叙事的技术汇报。推荐暖色系配色，冷色亦可。

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

> v2.3 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰和
> 语义配色。下方 `{PRIMARY}` 等页面模板保留用于旧版/第三方兼容，不是 v2.3 的主组合路径。

## 视觉元素

- **背景纹样**：封面铺细线几何放射纹样（圆弧网格、六边形，{SECONDARY}线条），内容页浅底
- **2.5D等距插画**：分层平台立体块（中性色为主、核心层{PRIMARY}发光）、服务器/盾牌等实物感插画
- **图标**：细线描，{PRIMARY}或深灰单色；卡片内图标带{PRIMARY}淡描边方框
- **流程卡片**：白色圆角卡片+{PRIMARY}淡描边+{PRIMARY}粗箭头串联
- **装饰**：角落几何符号，克制使用

## 布局规范

- 中低密度，留白充足
- 骨架：三段式流程（卡→箭头→卡）、左右对分（插画侧+文字侧）、2.5D分层塔+左侧标签
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

### 流程页（三步卡片）
```
Create a PPT content slide, 16:9, line illustration style. [COLOR_SCHEME]
标题：[标题]（{TITLE}粗体，可带{PRIMARY}引导词）。三个白色圆角卡片横排（{PRIMARY}淡描边），
卡间{PRIMARY}粗箭头；每卡=线描图标+{PRIMARY}小标题+3-4条{BODY}要点。等高对齐。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（2.5D分层）、ref-03（流程卡片）
