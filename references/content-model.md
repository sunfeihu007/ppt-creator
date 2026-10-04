# 内容计划 v3.0

`plan.json` 是唯一事实源；完整可运行样例见 `examples/content-plan.json`。
本版本有意移除旧视觉 schema，不默默继承旧风格、页面类型或生图配置。

## 层级

```text
整套 deck
└─ 大块 sections[]
   └─ 小块 blocks[]
      └─ 页面 pages[]（通过 block_id 归属，数组顺序为讲述顺序）
         └─ 信息实体 information_structure.entities[]
```

| 对象 | 必填内容（对应阶段确认时） |
|:--|:--|
| deck | id、title、audience、scenario、objective、thesis、focus、narrative、scope、takeaways[]、duration_minutes |
| section | id、title、thesis、focus、role_in_deck、priority；第二轮起有 blocks[] |
| block | id、title、thesis、focus、role_in_deck、role_in_parent、priority、key_points[] |
| page | id、block_id、title、thesis、focus、role_in_deck、role_in_parent、priority、audience_question、key_points[]、minutes、notes、information_structure；除最后一页外有 transition |

`title` 是主题，`thesis` 是希望听众记住的完整主张；`focus` 是本节点最应被强调的信息。
`role_in_deck` 说明为什么需要它、如何服务整体目标；`role_in_parent` 说明在直接所属内容块中的作用。
`priority` 为 `core / supporting / context`，分别是核心重点、支撑内容、背景/过渡。
整套至少有一个核心大块，每个大块至少有一个核心小块。
`out_of_scope[]` 可记录本节点不展开的内容，`evidence[]` 记录页级证据。

所有层级 id 在全篇唯一，以字母开头，其余使用英文、数字、下划线或短横线。页内实体 id 仅在本页唯一。
初始草稿允许部分字段暂缺，但字段类型和引用不能损坏。确认 Gate 再检查本阶段内容是否齐备。

## 关系

顶层 `relations[]` 是大块、小块、页面或跨层之间的语义关系，与所属层级不同：

```json
{"from":"S1", "to":"S2", "type":"supports", "reason":"问题诊断给出了方案应满足的约束"}
```

| type | 方向语义 |
|:--|:--|
| sequence | 前者先于/推进到后者，不自动表示因果 |
| cause | 前者引起后者，必须有事实或标注的假设依据 |
| supports | 前者的证据或判断支撑后者 |
| contrast | 比较前后两者；方向用于讲述顺序 |
| depends_on | 前者依赖后者（箭头不代表时间方向） |
| parallel | 并列维度；方向用于讲述顺序 |
| part_of | 前者是后者的一部分 |
| summary | 前者归纳为后者 |

每条关系必须有非空 `reason`。同层大块之间、同一大块的小块之间必须形成可解释的连通关系；
不能用“彼此无关”掩盖叙事缺口。合理并列也是关系，不要求所有逻辑图都是单向链或禁止正常反馈。
逐页讲述顺序由 `pages[]` 与 `transition` 表达，额外的证明/跨页关系写入 `relations`。

## 页内信息结构

```json
{
  "kind": "comparison",
  "entities": [
    {"id":"A", "label":"现状", "detail":"责任需要临时寻找"},
    {"id":"B", "label":"建议机制", "detail":"预先定义责任及升级路径"}
  ],
  "relations": [{"from":"A","to":"B","type":"contrast","reason":"比较责任如何被确定"}],
  "reading_order": ["A","B"],
  "dimensions": ["责任明确程度", "升级触发条件"]
}
```

`kind` 为 `statement / sequence / comparison / hierarchy / causal / data / story / list`。
实体必须有 `id/label/detail`（detail 可为空），阅读顺序恰好覆盖所有实体。
多实体需明确所有实体的关系；对比还需至少两个实体和比较维度。
这里只记录概念、数据、方向、关系和阅读顺序，不填写配色、坐标、卡片布局或图片提示词。

## 阶段、事实约束与输出

- `assurance_profile`：standard / client-facing / evidence-sensitive。
- `requirements[]`、`claim_constraints[]`、`sources[]`：见 `project-contract.md`。
- `open_questions[]`：`{"question":"待解决问题","blocking":true,"stage":"pages"}`；
  对相应及下游阶段生效，非阻塞项可保留但必须披露。
- `reviews`：工具维护的用户确认依据及内容指纹。不要手工填写或借样例伪造确认。
- v3 的默认交付是内容大纲、互动 HTML 和 JSON 内容交接，不再使用 `raster_slide` 或 `delivery_mode`。

## 最小第一轮草稿

```json
{
  "schema_version":"3.0",
  "deck": {
    "id":"DECK", "title":"协作机制改进", "audience":"部门负责人",
    "scenario":"内部决策讨论", "objective":"同意验证新的协作机制",
    "thesis":"先验证责任和升级机制，再讨论扩大范围", "focus":"低成本验证",
    "narrative":"先澄清问题，再定义验证路径", "scope":"仅讨论试点，不承诺效果",
    "takeaways":["先明确责任再试点"], "duration_minutes":10
  },
  "sections":[{
    "id":"S1", "title":"试点逻辑", "thesis":"机制是否有效需要通过试点验证",
    "focus":"验证判断", "role_in_deck":"说明为何提出试点决策", "priority":"core", "blocks":[]
  }],
  "pages":[], "relations":[]
}
```

此草稿可确认 outline；补齐小块后才能确认 content，补齐逐页内容后才能确认 pages。

## 从旧版本迁移

v3 是内容模型的破坏性升级。旧 `ppt_workspace/plan.json` 先保留原件，在新 workspace 建立 v3 草稿：

1. 继承旧 topic、audience、页面 title、points、notes 及真实需求/声明/来源，映射到新字段；
2. 与用户梳理大块/小块及角色、主旨、重点、关系，不能从旧模板或图片风格猜测内容逻辑；
3. 旧 `source_registry` 映射为 `sources`，保留 title 和准确 locator；旧 `affected_pages` 映射为 applies_to；
4. 补齐页内信息结构和逐页衔接，将旧事实声明整理到 evidence；
5. 丢弃视觉/生图/图片复用字段；旧图片批准记录不能当成新内容确认；
6. 校验并在原对话明确确认依据仍有效时记录确认，否则合并请求用户确认。

工具不会覆盖旧文件，也不会把缺失的内容结构自动编造出来。旧版本实现仍可从 Git 历史查看。
