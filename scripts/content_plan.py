"""Content-only planning schema, semantic checks and confirmation fingerprints."""
from copy import deepcopy
import hashlib
import json
import math
import re

VERSION = '3.0'
STAGES = ('outline', 'content', 'pages')
PRIORITIES = {'core', 'supporting', 'context'}
RELATIONS = {'sequence', 'cause', 'supports', 'contrast', 'depends_on', 'parallel', 'part_of', 'summary'}
FORMS = {'statement', 'sequence', 'comparison', 'hierarchy', 'causal', 'data', 'story', 'list'}
VISUAL_FIELDS = {'palette', 'style', 'industry', 'template', 'page_type', 'layout_hint', 'provider',
                 'image_transport', 'image_model', 'prompt_file', 'image', 'delivery_mode',
                 'reused_from', 'reuse_mode'}
COMMON = ('title', 'thesis', 'focus', 'role_in_deck')
DECK_FIELDS = ('title', 'audience', 'scenario', 'objective', 'thesis', 'focus', 'narrative', 'scope')
LABELS = {'sequence': '递进/先后', 'cause': '因果', 'supports': '支撑', 'contrast': '对比',
          'depends_on': '依赖', 'parallel': '并列', 'part_of': '组成', 'summary': '归纳'}
PRIORITY_LABELS = {'core': '核心重点', 'supporting': '支撑内容', 'context': '背景/过渡'}


class PlanError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def _array(value, label):
    if not isinstance(value, list):
        raise PlanError(f'{label} 必须是数组')
    return value


def _object(value, label):
    if not isinstance(value, dict):
        raise PlanError(f'{label} 必须是对象')
    return value


def _text(value, label, required=False):
    if not isinstance(value, str) or (required and not value.strip()):
        raise PlanError(f'{label} 必须是{"非空" if required else ""}文本')


def _strings(value, label):
    for item in _array(value, label):
        _text(item, label, True)


def nodes(plan):
    result = {plan['deck']['id']: ('deck', plan['deck'], None)}
    for section in plan['sections']:
        result[section['id']] = ('section', section, plan['deck']['id'])
        for block in section['blocks']:
            result[block['id']] = ('block', block, section['id'])
    for page in plan['pages']:
        result[page['id']] = ('page', page, page['block_id'])
    return result


def _links(links, allowed, label):
    seen = set()
    for link in _array(links, label):
        _object(link, label)
        for key in ('from', 'to', 'type', 'reason'):
            _text(link.get(key), f'{label}.{key}', True)
        if link['from'] not in allowed or link['to'] not in allowed:
            raise PlanError(f'{label} 引用了不存在的节点')
        if link['from'] == link['to']:
            raise PlanError(f'{label} 不允许自引用')
        if link['type'] not in RELATIONS:
            raise PlanError(f'{label} 未知关系类型：{link["type"]}')
        signature = (link['from'], link['to'], link['type'])
        if signature in seen:
            raise PlanError(f'{label} 存在重复关系')
        seen.add(signature)


def normalize(raw):
    """Validate shape without demanding that a work-in-progress has all content."""
    plan = deepcopy(_object(raw, 'plan'))
    if plan.get('schema_version', VERSION) != VERSION or 'deck' not in plan:
        raise PlanError('需要 v3 内容计划（deck/sections/pages）；旧计划请保留原件，按 references/content-model.md 迁移。')
    plan['schema_version'] = VERSION
    for name, default in [('sections', []), ('pages', []), ('relations', []),
                          ('requirements', []), ('claim_constraints', []), ('sources', []),
                          ('open_questions', []), ('reviews', {})]:
        plan.setdefault(name, deepcopy(default))
    plan.setdefault('assurance_profile', 'standard')
    if plan['assurance_profile'] not in {'standard', 'client-facing', 'evidence-sensitive'}:
        raise PlanError('未知 assurance_profile')
    _object(plan['deck'], 'deck')
    plan['deck'].setdefault('id', 'DECK')
    _object(plan['reviews'], 'reviews')
    for stage, review in plan['reviews'].items():
        if stage not in STAGES:
            raise PlanError(f'未知确认阶段：{stage}')
        _object(review, 'review')
        for key in ('fingerprint', 'note'):
            _text(review.get(key), f'review.{key}', True)
        if review.get('confirmed_by') != 'user':
            raise PlanError('确认记录必须来自用户')
    ids = set()

    def register(item, label):
        _object(item, label)
        ident = item.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', ident):
            raise PlanError(f'{label}.id 应为字母开头的英文/数字/下划线/短横线')
        if ident in ids:
            raise PlanError(f'重复 id：{ident}')
        ids.add(ident)
        if VISUAL_FIELDS.intersection(item):
            raise PlanError(f'{ident} 含旧视觉字段：{sorted(VISUAL_FIELDS.intersection(item))}')
        for field in (*COMMON, 'role_in_parent', 'audience_question', 'notes', 'transition',
                      'scenario', 'audience', 'objective', 'narrative', 'scope'):
            if field in item:
                _text(item[field], f'{ident}.{field}')
        for field in ('key_points', 'takeaways', 'out_of_scope'):
            if field in item:
                _strings(item[field], f'{ident}.{field}')
        if 'priority' in item and item['priority'] not in PRIORITIES:
            raise PlanError(f'{ident}.priority 必须为 core/supporting/context')
        for field in ('duration_minutes', 'minutes'):
            if field in item:
                n = item[field]
                if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or n <= 0:
                    raise PlanError(f'{ident}.{field} 必须为有限正数')

    if VISUAL_FIELDS.intersection(plan):
        raise PlanError('v3 不接受旧视觉配置；请使用内容计划 schema')
    register(plan['deck'], 'deck')
    for section in _array(plan['sections'], 'sections'):
        register(section, 'section')
        section.setdefault('blocks', [])
        for block in _array(section['blocks'], 'blocks'):
            register(block, 'block')
    block_ids = {b['id'] for s in plan['sections'] for b in s['blocks']}
    for page in _array(plan['pages'], 'pages'):
        register(page, 'page')
        if not isinstance(page.get('block_id'), str) or page['block_id'] not in block_ids:
            raise PlanError(f'{page["id"]} 的 block_id 不存在')
        structure = page.get('information_structure')
        if structure is not None:
            _object(structure, 'information_structure')
            for field in ('entities', 'relations', 'reading_order', 'dimensions'):
                structure.setdefault(field, [])
            if structure.get('kind') not in FORMS:
                raise PlanError(f'{page["id"]} 未知信息结构类型')
            unit_ids = set()
            for unit in _array(structure.get('entities', []), 'entities'):
                _object(unit, 'entity')
                for key in ('id', 'label', 'detail'):
                    _text(unit.get(key), f'entity.{key}', key != 'detail')
                if unit['id'] in unit_ids:
                    raise PlanError(f'{page["id"]} 信息实体 id 重复')
                unit_ids.add(unit['id'])
            _links(structure.get('relations', []), unit_ids, f'{page["id"]}.information_structure.relations')
            order = structure.get('reading_order', [])
            _strings(order, 'reading_order')
            if len(order) != len(set(order)) or set(order) != unit_ids:
                raise PlanError(f'{page["id"]}.reading_order 必须恰好覆盖所有信息实体')
            _strings(structure.get('dimensions', []), 'dimensions')
    index = nodes(plan)
    _links(plan['relations'], index, 'relations')
    source_ids = set()
    for source in _array(plan['sources'], 'sources'):
        _object(source, 'source')
        for field in ('id', 'title', 'locator'):
            _text(source.get(field), f'source.{field}', True)
        if source['id'] in source_ids:
            raise PlanError(f'来源 id 重复：{source["id"]}')
        source_ids.add(source['id'])
    for page in plan['pages']:
        for evidence in _array(page.get('evidence', []), 'evidence'):
            _object(evidence, 'evidence')
            _text(evidence.get('claim'), 'evidence.claim', True)
            if evidence.get('status') not in {'verified', 'hypothesis', 'needs_source'}:
                raise PlanError('证据状态必须为 verified/hypothesis/needs_source')
            _strings(evidence.get('source_refs', []), 'source_refs')
            if not set(evidence.get('source_refs', [])) <= source_ids:
                raise PlanError(f'{page["id"]} 引用了不存在的来源')
            _text(evidence.get('note', ''), 'evidence.note')
    rule_ids = set()
    for collection in ('requirements', 'claim_constraints'):
        for rule in _array(plan[collection], collection):
            _object(rule, collection)
            for key in ('id', 'text'):
                _text(rule.get(key), f'{collection}.{key}', True)
            if rule['id'] in rule_ids:
                raise PlanError(f'规则 id 重复：{rule["id"]}')
            rule_ids.add(rule['id'])
            for key in ('applies_to', 'required_terms', 'forbidden_terms'):
                _strings(rule.get(key, []), f'{collection}.{key}')
            if not set(rule.get('applies_to', [])) <= set(index):
                raise PlanError(f'{rule["id"]} 引用了不存在的适用节点')
    for question in _array(plan['open_questions'], 'open_questions'):
        _object(question, 'open_question')
        _text(question.get('question'), 'open_question.question', True)
        if not isinstance(question.get('blocking'), bool):
            raise PlanError('open_question.blocking 必须为布尔值')
        if question.get('stage') not in STAGES:
            raise PlanError('open_question.stage 必须为 outline/content/pages')
    return plan


def projection(plan, stage):
    level = STAGES.index(stage)
    sections = [{k: v for k, v in s.items() if k != 'blocks'} for s in plan['sections']]
    ids = {plan['deck']['id'], *(s['id'] for s in sections)}
    value = {'deck': plan['deck'], 'sections': sections, 'assurance_profile': plan['assurance_profile']}
    if level >= 1:
        value['sections'] = plan['sections']
        ids.update(b['id'] for s in plan['sections'] for b in s['blocks'])
        for key in ('requirements', 'claim_constraints', 'sources'):
            value[key] = plan[key]
    if level >= 2:
        value['pages'] = plan['pages']
        ids.update(p['id'] for p in plan['pages'])
    value['relations'] = [r for r in plan['relations'] if r['from'] in ids and r['to'] in ids]
    value['open_questions'] = [q for q in plan['open_questions'] if STAGES.index(q['stage']) <= level]
    return value


def review_status(plan):
    result, upstream = {}, True
    for stage in STAGES:
        record = plan['reviews'].get(stage)
        own = bool(record and record['fingerprint'] == digest(projection(plan, stage)))
        current = own and upstream
        result[stage] = 'confirmed' if current else ('stale' if record else 'pending')
        upstream = current
    return result


def lint(plan, stage='pages'):
    plan = normalize(plan)
    findings = []
    level = STAGES.index(stage)
    index = nodes(plan)

    def add(node, message, severity='error'):
        findings.append({'severity': severity, 'node': node, 'message': message})

    def required(node, fields):
        for field in fields:
            value = node.get(field)
            if value is None or value == [] or (isinstance(value, str) and not value.strip()):
                add(node['id'], f'缺少 {field}')

    def connected(group, label):
        if len(group) < 2:
            return
        adjacency = {ident: set() for ident in group}
        for relation in plan['relations']:
            a, b = relation['from'], relation['to']
            if a in group and b in group:
                adjacency[a].add(b)
                adjacency[b].add(a)
        visited, todo = set(), [next(iter(group))]
        while todo:
            ident = todo.pop()
            if ident not in visited:
                visited.add(ident)
                todo.extend(adjacency[ident] - visited)
        if visited != group:
            add(label, '同层内容关系未连通；补充各块之间有理由的逻辑关系')

    required(plan['deck'], (*DECK_FIELDS, 'duration_minutes', 'takeaways'))
    if not plan['sections']:
        add('DECK', '至少需要一个大块')
    if plan['sections'] and not any(s.get('priority') == 'core' for s in plan['sections']):
        add('DECK', '明确至少一个核心大块（priority=core）')
    connected({s['id'] for s in plan['sections']}, 'DECK')
    for kind, node, parent in index.values():
        if kind == 'deck' or (kind == 'block' and level < 1) or (kind == 'page' and level < 2):
            continue
        required(node, (*COMMON, 'priority'))
        if kind in {'block', 'page'}:
            required(node, ('role_in_parent', 'key_points'))
        if kind == 'section' and level >= 1:
            if not node['blocks']:
                add(node['id'], '大块中至少需要一个小块')
            elif not any(b.get('priority') == 'core' for b in node['blocks']):
                add(node['id'], '明确此大块的核心小块')
            connected({b['id'] for b in node['blocks']}, node['id'])
        if kind == 'block' and level >= 2 and not any(p['block_id'] == node['id'] for p in plan['pages']):
            add(node['id'], '小块尚未分配页面')
        if kind == 'page':
            required(node, ('audience_question', 'minutes', 'information_structure', 'notes'))
            structure = node.get('information_structure', {})
            entities = structure.get('entities', [])
            if not entities:
                add(node['id'], '需要明确页内信息实体，供后续信息图设计')
            if len(entities) > 1:
                linked = {r[k] for r in structure.get('relations', []) for k in ('from', 'to')}
                if linked != {e['id'] for e in entities}:
                    add(node['id'], '页内实体存在未说明的关系')
            if structure.get('kind') == 'comparison' and (len(entities) < 2 or not structure.get('dimensions')):
                add(node['id'], '对比内容需要至少两个对象和明确的比较维度')
            for evidence in node.get('evidence', []):
                if evidence['status'] == 'verified' and not evidence.get('source_refs'):
                    add(node['id'], '已证实的声明必须引用来源')
                if evidence['status'] == 'hypothesis' and not evidence.get('note', '').strip():
                    add(node['id'], '假设/示意必须写明边界说明')
                if evidence['status'] == 'needs_source':
                    add(node['id'], f'待补充来源：{evidence["claim"]}',
                        'error' if plan['assurance_profile'] == 'evidence-sensitive' else 'warning')
    if level >= 2:
        if not plan['pages']:
            add('DECK', '没有逐页内容')
        for page in plan['pages'][:-1]:
            if not page.get('transition', '').strip():
                add(page['id'], '需要说明如何承接下一页（transition）')
        total = sum(p.get('minutes', 0) for p in plan['pages'])
        duration = plan['deck'].get('duration_minutes', 0)
        if duration and abs(total - duration) > max(1, duration * .2):
            add('DECK', f'逐页时长合计 {total:g} 分钟，目标 {duration:g} 分钟；请调整或解释', 'warning')
        titles = [p.get('thesis') for p in plan['pages'] if p.get('thesis')]
        if len(titles) != len(set(titles)):
            add('DECK', '存在相同页面主旨，请检查重复内容与页面必要性', 'warning')
    for question in plan['open_questions']:
        if question['blocking'] and STAGES.index(question['stage']) <= level:
            add('DECK', f'待解决问题：{question["question"]}')
    for collection in ('requirements', 'claim_constraints'):
        if level < 1:
            continue
        for rule in plan[collection]:
            # An empty scope applies once to the complete plan. A section/block scope
            # checks its subtree; page-specific required terms are never imposed globally.
            scopes = rule.get('applies_to') or [plan['deck']['id']]
            for scope in scopes:
                descendants = {scope}
                for ident, (_, _, parent) in index.items():
                    if parent in descendants:
                        descendants.add(ident)
                text = '\n'.join(json.dumps({k: v for k, v in n.items() if k != 'blocks'}, ensure_ascii=False)
                                 for ident, (kind, n, _) in index.items() if ident in descendants
                                 and not (kind == 'page' and level < 2))
                if index[scope][0] == 'page' and level < 2:
                    continue
                for term in rule.get('required_terms', []):
                    if term not in text:
                        add(scope, f'{rule["id"]} 缺少必需词：{term}')
                for term in rule.get('forbidden_terms', []):
                    if term in text:
                        add(scope, f'{rule["id"]} 命中禁止词：{term}')
    return findings


def confirm(plan, stage, note):
    plan = normalize(plan)
    _text(note, '确认依据', True)
    statuses = review_status(plan)
    for previous in STAGES[:STAGES.index(stage)]:
        if statuses[previous] != 'confirmed':
            raise PlanError(f'请先完成用户对 {previous} 的确认')
    errors = [f for f in lint(plan, stage) if f['severity'] == 'error']
    if errors:
        raise PlanError('\n'.join(f'{f["node"]}: {f["message"]}' for f in errors))
    plan['reviews'][stage] = {'fingerprint': digest(projection(plan, stage)),
                              'confirmed_by': 'user', 'note': note}
    return plan
