# 风格：现代卡片（card-modern）——颜色无关

> 版式来源：奇瑞商用车交流方案。折页卡片+超大数字+黑线插画，年轻利落，
> 适合客户交流、销售方案、路演。

## 视觉元素

- **折页卡片**：带折角的白色卡片，顶部{PRIMARY}小图标（目录页标志元素）
- **超大数字**：{PRIMARY}特粗 01/02/03/04 与{TITLE}标题并置
- **单色线插画**：深色单线描实物，{PRIMARY}小色块局部填充点缀
- **品牌位**：左上/右上留logo空白区（后期贴真logo，禁止生成假logo）
- **样机展示**：设备样机斜排，屏幕为浅灰占位（截图后期贴入）
- **页脚**：页码+一行小字，全篇统一

## 布局规范

- 中密度；目录页 1+4 结构（左概览卡+右四折页卡）
- 标题行："{PRIMARY}竖块/引导词+{TITLE}主标题"，通栏细灰线
- 架构页：横向分层，每层左侧{SECONDARY}标签条+白色功能卡片
- 卡片小圆角，比玻璃风更利落

## 页面类型模板

### 封面页
```
Create a modern business PPT cover slide, 16:9, clean card style. [COLOR_SCHEME]
左侧：{TITLE}特大粗体标题[主题]+{BODY}副标题+{PRIMARY}粗体日期/场合词。
右侧：深色单线描插画（[主题相关]）+{PRIMARY}色块点缀+浅灰几何底台。左上留logo空白区。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 目录页（1+4折页卡）
```
Create a modern PPT contents slide, 16:9. [COLOR_SCHEME]
标题行：{PRIMARY}引导词+{TITLE}粗体主题句+通栏细灰线。左侧一张灰白概览卡；
右侧四张白色折页卡横排（右上折角）：{PRIMARY}特大序号+{PRIMARY}小图标+{TITLE}粗体条目名+
三行{BODY}说明。等高对齐。
Layout reference: attached image (layout only, IGNORE its colors).
```

### 架构页（横向分层）
```
Create a modern PPT architecture slide, 16:9. [COLOR_SCHEME]
标题：{PRIMARY}引导块+{TITLE}粗体。[N]个横向分层：左侧{SECONDARY}标签条（层名）+
层内2-3张白色圆角功能卡（细灰描边、小图标+名称+一行说明），层间细灰箭头。
背景极淡等距网格。严格对齐。
Layout reference: attached image (layout only, IGNORE its colors).
```

参考图：ref-01（封面）、ref-02（1+4目录）、ref-03（横向分层）
