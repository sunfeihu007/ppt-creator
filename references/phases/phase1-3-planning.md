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
3. 确认后生成 draft_plan.json 并执行 `python scripts/plan_tool.py init --file draft_plan.json`。

draft_plan.json 格式：
```json
{
  "topic": "主题", "audience": "受众",
  "pages": [
    {"id":"P01","template":"cover","title":"主题","subtitle":"副标题","points":[],"notes":"【过渡页】1-2分钟…"},
    {"id":"P02","template":"toc","title":"目录","points":["部分1","部分2"],"notes":"…"},
    {"id":"P03","template":"transition","title":"第一部分 …","points":[],"notes":"…"},
    {"id":"P04","template":"content","title":"页标题","points":["要点1","要点2"],"layout_hint":"三栏卡片","notes":"【重点页】5-6分钟…"},
    {"id":"P05","template":"arch","title":"…","points":["…"],"layout_hint":"分层架构","notes":"…"}
  ]
}
```
template 取值：cover/toc/transition/content/arch/flow/compare/case/summary/end
（transition/summary/end 复用 cover 或 content 模板骨架，layout_hint 说明差异）。
