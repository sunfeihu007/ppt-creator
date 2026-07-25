# 风格：工业图解（industrial-diagram）——颜色无关

> 来源方向：Diagram-Driven Isotype、工程系统图、制造业技术图册。适合港口码头、
> 汽车制造、工业 AI、设备与系统关系密集的解决方案。

## 风格提示词骨架

```
Create a premium 16:9 presentation slide in an industrial engineering-diagram family.
[COLOR_SCHEME]
Use a precise modular grid, orthogonal connectors, compact technical labels, consistent
machine/system linework, square or very-small-radius modules and restrained engineering
annotation marks. Keep surfaces flat and diagrams legible; use depth only as a subtle
layer cue, never as decorative 3D. Use one structural color and one small safety/focal
color. No sci-fi HUD chrome, no neon glow, no fictional gauge cluster, no cartoon robot,
no heavy metallic gradient and no generic rounded-card dashboard.
```

## 视觉语法

- **网格**：工程模块网格；水平、垂直基线清晰。
- **字体**：无衬线正文＋等宽小标签，中文标题保持简洁。
- **几何**：矩形、轨道、阶段门、设备轮廓；圆角极小。
- **连接**：正交线、统一箭头、明确起止点，避免交叉穿字。
- **颜色**：结构色覆盖主要模块，安全/聚焦色只标关键节点。
- **图片**：真实现场、设备、产线或产品图片采用直角裁切和技术标注。
- **图标**：单色设备/业务线描，不使用彩色徽章。
- **签名元素**：工程编号、坐标刻度、细分区线和模块化节奏。

## 页面类型模板（旧版 make_prompt.py 兼容）

### 封面页
```
Create an industrial-diagram PPT cover, 16:9. [COLOR_SCHEME]
左侧标题系统，右侧一个真实设备/场景轮廓或模块化工程图，叠加极淡坐标网格和一处聚焦标记。
```

### 架构图页
```
Create an industrial system architecture slide, 16:9. [COLOR_SCHEME]
使用分层矩形模块、正交连接线、统一技术标签和单一关键节点高亮；无发光HUD、无装饰3D。
```

### 详解页
```
Create an industrial detail slide, 16:9. [COLOR_SCHEME]
主模块拆解图配窄注释栏，使用工程编号、发丝引导线和小面积聚焦色，保持充分留白和可读性。
```

## 使用边界

- 技术标签只表达用户提供的真实内容，不生成虚构参数。
- 允许轻度工程仪表感，但不得发展成深色科幻 HUD。
- 不使用金属光泽表达“工业”，工业感来自结构、线条、比例和真实素材。
