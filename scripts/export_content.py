"""Export the same content plan as Markdown and a self-contained interactive HTML."""
import html
import json
from pathlib import Path

from content_plan import LABELS, PRIORITY_LABELS, digest, lint, nodes, review_status

ASSETS = Path(__file__).with_name('assets')
STAGE_LABELS = {'outline': '大纲分块', 'content': '小块与关系', 'pages': '逐页内容'}
STATUS_LABELS = {'confirmed': '已确认', 'pending': '待确认', 'stale': '修改后待重新确认'}


def markdown(plan, draft=False):
    index = nodes(plan)
    statuses = review_status(plan)
    deck = plan['deck']
    lines = [f'# {deck.get("title", "内容规划")} — 内容大纲', '',
             f'状态：{"草稿 · 不可进入版式设计" if draft else "内容已确认 · 可交接后续设计"}',
             f'内容版本：`{digest({k: v for k, v in plan.items() if k != "reviews"})}`', '',
             '## 整体叙事', '']
    for label, key in [('受众', 'audience'), ('使用场景', 'scenario'), ('沟通目标/期望行动', 'objective'),
                       ('整套核心主张', 'thesis'), ('整套重点', 'focus'), ('叙事主线', 'narrative'),
                       ('内容边界', 'scope'), ('目标时长（分钟）', 'duration_minutes')]:
        lines.append(f'- **{label}**：{deck.get(key, "待补充")}')
    lines += ['- **听众应记住**：' + '；'.join(deck.get('takeaways', [])), '']
    lines += ['## 确认记录', '']
    for stage, status in statuses.items():
        lines += [f'- {STAGE_LABELS[stage]}：{STATUS_LABELS[status]}']
        if stage in plan['reviews']:
            lines += [f'  - 用户确认依据：{plan["reviews"][stage]["note"]}']
    lines += ['', '## 大块与小块内容', '']

    def describe(node, parent_label=None):
        result = []
        for label, key in [('主旨', 'thesis'), ('重点', 'focus'), ('在整套 PPT 中的作用', 'role_in_deck')]:
            result.append(f'- **{label}**：{node.get(key, "待补充")}')
        if parent_label:
            result.append(f'- **在{parent_label}中的作用**：{node.get("role_in_parent", "待补充")}')
        result += [f'- **内容优先级**：{PRIORITY_LABELS.get(node.get("priority"), "待补充")}']
        return result

    for section in plan['sections']:
        lines += [f'### {section["id"]} · {section.get("title", "待定")}', '', *describe(section), '']
        for block in section['blocks']:
            lines += [f'#### {block["id"]} · {block.get("title", "待定")}', '', *describe(block, '大块')]
            lines += ['- **小块要点**：' + '；'.join(block.get('key_points', []))]
            pages = [p['id'] for p in plan['pages'] if p['block_id'] == block['id']]
            lines += ['- **对应页面（按讲述顺序）**：' + ' → '.join(pages), '']
    lines += ['## 层间与同层逻辑关系', '', '箭头按记录的关系方向阅读；依赖表示“前者依赖后者”。', '']
    for relation in plan['relations']:
        a, b = relation['from'], relation['to']
        lines += [f'- **{a} {index[a][1].get("title", "")} → {b} {index[b][1].get("title", "")}**'
                  f' · {LABELS[relation["type"]]}：{relation["reason"]}']
    lines += ['', '## 逐页内容（演讲顺序）', '']
    for number, page in enumerate(plan['pages'], 1):
        block = index[page['block_id']][1]
        section = index[index[page['block_id']][2]][1]
        lines += [f'### {number:02d} / {page["id"]} · {page.get("title", "待定")}', '',
                  f'归属：{section.get("title", "")} → {block.get("title", "")}', '', *describe(page, '小块'),
                  f'- **听众的问题**：{page.get("audience_question", "待补充")}',
                  f'- **建议时长**：{page.get("minutes", "待定")} 分钟', '', '**需要表达的内容**', '']
        lines += [f'- {point}' for point in page.get('key_points', [])]
        structure = page.get('information_structure', {})
        lines += ['', '**供后续信息图设计使用的信息结构（尚未指定版式）**', '',
                  f'- 内容关系类型：{structure.get("kind", "待定")}',
                  '- 阅读顺序：' + ' → '.join(structure.get('reading_order', []))]
        if structure.get('dimensions'):
            lines += ['- 比较维度：' + '、'.join(structure['dimensions'])]
        for entity in structure.get('entities', []):
            lines += [f'- 信息实体 {entity["id"]}：{entity["label"]} — {entity["detail"]}']
        for relation in structure.get('relations', []):
            lines += [f'- {relation["from"]} → {relation["to"]} · {LABELS[relation["type"]]}：{relation["reason"]}']
        lines += ['', '**事实与依据**', '']
        if not page.get('evidence'):
            lines += ['- 未登记外部事实声明；制作时不得自行添加数据或实证。']
        for evidence in page.get('evidence', []):
            lines += [f'- {evidence["claim"]}（{evidence["status"]}）；来源：'
                      + ', '.join(evidence.get('source_refs', [])) + f'；边界：{evidence.get("note", "")}']
        lines += ['', f'**讲述提示**：{page.get("notes", "待补充")}', '',
                  f'**承接下一页**：{page.get("transition", "结束 / 待定")}', '']
    lines += ['## 需求、声明边界与来源', '']
    for collection in ('requirements', 'claim_constraints'):
        for rule in plan[collection]:
            lines += [f'- {rule["id"]}：{rule["text"]}；适用：{", ".join(rule.get("applies_to", [])) or "全篇"}',
                      '- 必需词：' + '、'.join(rule.get('required_terms', [])) + '；禁止词：' + '、'.join(rule.get('forbidden_terms', []))]
    for source in plan['sources']:
        lines += [f'- {source["id"]} · {source["title"]}：{source["locator"]}']
    lines += ['', '## 待解决问题与检查结果', '']
    lines += [f'- {q["question"]}（{"阻塞" if q["blocking"] else "非阻塞"}，{q["stage"]}）' for q in plan['open_questions']]
    findings = lint(plan)
    lines += [f'- [{f["severity"]}] {f["node"]}：{f["message"]}' for f in findings] or ['- 无机器检查发现；仍须人工检查论证质量、来源真实性与讲述节奏。']
    lines += ['', '## 后续设计交接', '',
              '仅在三轮内容确认有效且阻塞项清零后进入版面/版式设计。',
              '依据每页主旨、重点、信息实体、关系和阅读顺序选择信息图表达；不预设风格、配色或模板。',
              '设计不得改变已确认的论点、数据含义、章节作用和因果方向。内容变化后应重新导出并确认受影响阶段。', '']
    return '\n'.join(lines)


def render_html(plan, draft=False):
    payload = {'plan': plan, 'status': review_status(plan), 'draft': draft, 'findings': lint(plan),
               'relations': LABELS, 'priorities': PRIORITY_LABELS}
    # JSON is inert, but its script element must also be safe from closing tags.
    data = json.dumps(payload, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    data = data.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = (ASSETS / 'map.html').read_text(encoding='utf-8')
    return (template.replace('<!--TITLE-->', html.escape(plan['deck'].get('title', '内容规划')))
            .replace('/*INLINE_CSS*/', (ASSETS / 'map.css').read_text(encoding='utf-8'))
            .replace('/*INLINE_JS*/', (ASSETS / 'map.js').read_text(encoding='utf-8'))
            .replace('<!--PLAN_DATA-->', data))
