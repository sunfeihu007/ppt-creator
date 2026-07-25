# 设计系统索引（配色 × 风格 解耦版 v2）

> 放入仓库建议路径：`references/design/`（palettes/ + styles/ + 本文件）
> 核心思想：**配色（palette）管颜色，风格（style）管质感与版式，二者自由组合。**
> 生成提示词 = 风格模板骨架 + 配色文件的"提示词配色描述段"替换 `[COLOR_SCHEME]` + 颜色 Token 替换。

## 一、可用配色（palettes/）

| 配色 ID | 名称 | 主色 | 辅色 | 底色 | 备注 |
|:---|:---|:---|:---|:---|:---|
| `orange-teal` | 橙青绿 | 橙 `#E87818` | 深青绿 `#00655F` | 白 | ★公司默认配色 |
| `liantong-red` | 联通红 | 红 `#E60012` | 深灰 | 浅灰白 | 原 skill 默认 |
| `tech-blue` | 科技蓝 | 蓝 `#2B7BFF` | 中蓝 | 浅蓝白 | |
| `navy-gold` | 藏青金 | 藏青 `#0C2D4F` | 金 `#C9A254` | 纯白 | 高级稳重 |
| `warm-orange` | 暖橙 | 橙 `#EC6309` | 米色 | 米白暖调 | 温暖叙事 |
| `deep-space` | 深空青 | 荧光青 `#35E0C8` | 冰蓝 | 深藏青 | ⚠️唯一深色配色 |

## 二、可用风格（styles/，颜色无关）

| 风格 ID | 名称 | 质感关键词 | 信息密度 | 参考图 |
|:---|:---|:---|:---|:---|
| `glass-3d` | 玻璃拟态3D | 玻璃卡片、等距分层、渐变徽章 | 高 | 3张 |
| `flat-editorial` | 平面杂志排版 | 大色块、大数字、细线、留白 | 低中 | 3张 |
| `lineart-minimal` | 极简线描 | 单色细线插画、大留白 | 低 | 3张 |
| `illust-2.5d` | 2.5D插画 | 等距插画、几何线描纹样 | 中低 | 3张 |
| `card-modern` | 现代卡片 | 折页卡、超大数字、线插画 | 中 | 3张 |
| `hud-frame` | HUD线框 | 发光线框、扫描框、参数标签 | 中高 | 3张 |

## 三、组合兼容矩阵

| | glass-3d | flat-editorial | lineart-minimal | illust-2.5d | card-modern | hud-frame |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| orange-teal | ★★★ | ★★★ | ✕ | ★★★ | ★★★ | ✕ |
| liantong-red | ✕ | ★★ | ★★ | ★★ | ★★ | ✕ |
| tech-blue | ★★★ | ★★ | ★★★ | ★★ | ★★ | ✕ |
| navy-gold | ✕ | ★★★（原版） | ★★ | ✕ | ★★ | ✕ |
| warm-orange | ★★ | ★★ | ★★ | ★★★（原版） | ★★★ | ✕ |
| deep-space | ✕ | ✕ | ✕ | ✕ | ✕ | ★★★（原版） |

规则：✕ 为材质或颜色冲突，脚本会禁止选择；★数为推荐度（"原版"=该组合即抽取来源的
原始形态）。`compatibility.json` 是机器校验的唯一事实来源，本表必须与其同步。

## 四、默认与推荐（针对公司使用）

- **公司默认组合**：`orange-teal` × `glass-3d` —— 保留公司配色，把现有传统版式升级为玻璃科技质感；
- **高层汇报**：`orange-teal` × `flat-editorial`；
- **对外交流/销售**：`orange-teal` × `card-modern`；
- 用户未指定时：先问配色（默认橙青绿），再问风格（默认 glass-3d）。

## 五、双色配色使用要点

橙青绿遵守 85-12-3：中性色85% + 青绿结构12% + 橙色微强调3%。
橙=聚光灯（序号、重点、数据流），绿=骨架（图标、框架、标签条）。禁止两色平分画面。
单色配色（联通红、科技蓝）则辅色自动退化为深灰/同族浅色。

## 六、新增配色/风格检查

新增或删除 palette/style 后，必须为它与另一维的每个选项在 `compatibility.json` 中登记
`recommended`、`allowed` 或 `blocked`（禁用项必须写原因），然后运行：

```bash
python scripts/validate_design.py
```

验证器拒绝未登记组合，禁止以“默认兼容”放行。

## 七、参考图垫图规则（重要）

- 风格参考图在 `styles/<style>/ref-*.jpg`，携带的是**版式与质感**信息，但也携带了原配色；
- 因此垫图时提示词必须包含："Layout reference: attached image — follow its layout and
  texture, IGNORE its colors, use the specified color scheme instead"；
- 配色准确性靠文字描述段+hex 保证，不靠参考图；
- `palettes/orange-teal/ref-*.jpg` 仅供人工核对品牌色，不用于垫图。

## 八、全局约束（所有组合通用）

沿用 SKILL.md CRITICAL CONSTRAINTS：禁止色值/颜色名以文字出现在画面上、禁止占位符与假logo、
禁止乱码、整套 PPT 锁定同一"配色×风格×生图后端"组合、同类元素对齐、文字完整不截断。
