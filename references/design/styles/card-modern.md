# 风格：现代卡片（card-modern）——颜色无关

> 来源方向：模块化产品发布、销售方案与客户交流演示。折角模块、超大数字和单色线描，
> 年轻利落，但不把每一页都做成卡片墙。

## 风格提示词骨架

```
Create a professional 16:9 presentation slide in a clean modern modular-card family.
[COLOR_SCHEME]
Keep a stable editorial grid, bold numeric hierarchy, small-radius cards, restrained
hairline borders and consistent monochrome line icons. Cards are one container option,
not the default for every page. Use one folded-corner or clipped-corner detail as the
deck-wide signature. Avoid oversized soft bubbles, heavy shadows, decorative pills,
rainbow icons and generic dashboard density.
```

> v2.6 执行说明：`make_prompt.py` 使用上方整套骨架，再叠加标准页面类型、行业视觉修饰、
> 视觉治理和语义配色。下方模板只用于旧版/第三方兼容。

## 视觉元素

- **折页卡片**：带折角的白色卡片，顶部{PRIMARY}小图标（目录页标志元素）
- **超大数字**：只在真实顺序或关键数据存在时使用，不为了装饰虚构编号
- **单色线插画**：深色单线描实物，{PRIMARY}小色块局部填充点缀
- **真实素材**：真实截图或产品图采用一个主框；缺少素材时不画假界面或假设备样机
- **页脚**：只保留真实页码或用户提供的信息，全篇统一

## 布局规范

- 中密度；目录页用左侧概览＋右侧纵向条目，不建立卡片墙
- 标题行："{PRIMARY}竖块/引导词+{TITLE}主标题"，通栏细灰线
- 架构页：横向分层，每层左侧{SECONDARY}标签条+白色功能卡片
- 卡片小圆角，比玻璃风更利落

## 页面类型模板（旧版兼容）

### 封面页
```
Create a modern business PPT cover slide, 16:9, clean card style. [COLOR_SCHEME]
左侧：{TITLE}特大粗体标题[主题]+{BODY}副标题。
右侧：一个与主题直接相关的单色线描或真实产品图，配一处{PRIMARY}折角结构。
不得生成日期、Logo、版本号或设备界面占位。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 目录页（概览＋条目轴）
```
Create a modern PPT contents slide, 16:9. [COLOR_SCHEME]
标题行：{PRIMARY}引导词+{TITLE}粗体主题句+通栏细灰线。左侧一个概览模块；
右侧按真实条目数量建立纵向阅读轴，每项用序号、条目名和一行说明直接排版。
只在一处使用折角签名，不为每项配装饰图标。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 架构页（横向分层）
```
Create a modern PPT architecture slide, 16:9. [COLOR_SCHEME]
标题：{PRIMARY}引导块+{TITLE}粗体。[N]个横向分层：左侧{SECONDARY}标签条（层名）+
层内使用扁平功能模块（细灰描边、名称+一行说明），层间细灰箭头。
背景极淡等距网格。严格对齐。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（概览＋条目轴）、ref-03（横向分层）
