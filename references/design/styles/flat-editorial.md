# 风格：平面杂志排版（flat-editorial）——颜色无关

> 版式来源：宁波航交所知识中台建设方案（原生PPT）。
> 无3D无光效，靠字号对比、大数字、细线与留白建立高级感。最耐看、最不易过时。
> 同时适合生图路线与 python-pptx 原生绘制降级路线（无生图key时首选本风格）。

## 视觉元素

- **大色块**：封面左/右半幅 `{PRIMARY}` 斜切色块；内容页 `{PRIMARY}` 卡片头条
- **大数字序号**：目录超大 01–07 `{PRIMARY}` 数字 + 细灰分隔线 + 英文小标
- **细节点缀**：`{SECONDARY}` 只做细节——标题旁短竖线、小方块标签、分隔线、章节标
- **中英双语层级**：中文大标题 + 英文小字标注（CONTENTS、ARCHITECTURE 等）
- **页眉页脚**：统一章节编号页眉 + 页码页脚，全篇一致（杂志感的关键）
- **图标极少**：以排版为主，仅单色细线图标

## 布局规范

- 低中密度，留白是设计的一部分；严格网格对齐
- 骨架：目录左右对分；内容页N列卡片（{PRIMARY}头+白身）；场景页双栏大卡
- 信息三级：{SECONDARY}小标 → {PRIMARY}大标 → {BODY}说明

## 页面类型模板

### 封面页
```
Create a premium PPT cover slide, 16:9, flat editorial/magazine layout, NO 3D, NO glow.
[COLOR_SCHEME]
左侧60%为{PRIMARY}斜切大色块：{SECONDARY}短竖线+白色特大标题[主题]+白色细体副标题+
细{SECONDARY}线与落款[单位/日期]；右侧40%留白。构图克制高级。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 目录页
```
Create a PPT contents slide, 16:9, flat editorial layout. [COLOR_SCHEME]
左侧：{SECONDARY}小字CONTENTS+{PRIMARY}特大标题"汇报大纲"+一句{BODY}说明。
右侧：[N]个条目纵向排列：{PRIMARY}超大序号+条目名（{PRIMARY}粗体）+英文小标（灰细体）+
细灰分隔线。全部左对齐，大量留白。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 内容页（卡片矩阵）
```
Create a PPT content slide, 16:9, flat editorial layout. [COLOR_SCHEME]
页眉：{PRIMARY}小色块章节号+章节名+细灰通栏线。标题：[标题]（{PRIMARY}粗体+{SECONDARY}短竖线）。
[N]个卡片网格：{PRIMARY}色头条（白字：英文小标+中文名）+白色卡身（{SECONDARY}小字字段名+
{BODY}要点行）。严格等宽等高对齐。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（目录）、ref-03（卡片矩阵）
