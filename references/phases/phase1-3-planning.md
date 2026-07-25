# Phase 1–3：规划期详细指令

## Phase 1 需求理解与大纲讨论

目标：确定核心信息与3-5个主要部分。
1. 询问使用场景（汇报/介绍/培训/销售）、目标受众（领导/客户/同事/学生）、演讲时长（决定页数）；
2. 用户提供了文件夹/文档 → 先读取提取关键信息；
3. 讨论确定3-5个主要部分：每部分一个清晰主题，部分间逻辑递进
   （建议：引言/背景 → 核心内容2-3部分 → 总结/展望）。

输出格式：
```
## PPT大纲框架
- 主题：[…] - 受众：[…] - 预计页数：[X页]
- 主要部分：1.[…] 2.[…] 3.[…]
```
页数参考：15分钟≈12-15页；30分钟≈20-25页；1小时培训≈25-35页。
用户确认后：进入 Phase 2。

## Phase 2 内容方向讨论

逐部分讨论2-4个核心要点，确保要点间有逻辑关联（并列/递进/因果）；
询问是否有特别要强调的内容或数据。输出"## 内容规划"分部分要点列表。用户确认后进入 Phase 3。

## Phase 3 页数分配与 plan.json 创建

1. 每页聚焦一个核心观点；封面1页+目录1页+每部分(过渡页1+内容页2-4)+总结1+结束1；
2. 输出逐页清单（P01封面…）供用户确认；
3. 为每页选择与内容形状匹配的 `template`；必要时显式补充视觉 `page_type`；
4. 确认后生成 draft_plan.json 并执行 `python scripts/plan_tool.py init --file draft_plan.json`。

`page_type` 只描述页面的视觉构图类型，不新增或改写内容。行业视觉修饰在 Phase 4 选择，
不得在 Phase 1–3 因“港口/金融/制造”等行业名称自动增删章节、要点或案例。

draft_plan.json 格式：
```json
{
  "topic": "主题", "audience": "受众",
  "pages": [
    {"id":"P01","template":"cover","page_type":"cover","title":"主题","subtitle":"副标题","points":[],"notes":"【过渡页】1-2分钟…"},
    {"id":"P02","template":"toc","page_type":"toc","title":"目录","points":["部分1","部分2"],"notes":"…"},
    {"id":"P03","template":"transition","page_type":"section","title":"第一部分 …","points":[],"notes":"…"},
    {"id":"P04","template":"content","page_type":"detail","title":"页标题","points":["要点1","要点2"],"layout_hint":"主模块＋注释栏","notes":"【重点页】5-6分钟…"},
    {"id":"P05","template":"arch","page_type":"architecture","title":"…","points":["…"],"layout_hint":"分层架构","notes":"…"}
  ]
}
```

`template` 取值：
`cover/toc/transition/content/arch/flow/compare/case/summary/end/statement/overview/kpi/roadmap`。

标准 `page_type` 取值：
`cover/toc/section/overview/architecture/flow/detail/compare-kpi/case/roadmap/closing`。

`page_type` 可省略，`plan_tool.py` 会按 `template` 自动映射；显式填写时必须与页面实际视觉职责一致。
旧 draft_plan 与旧 plan.json 会自动补成标准页面类型，原字段保留不丢失。
