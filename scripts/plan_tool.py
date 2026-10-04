#!/usr/bin/env python3
"""Create, review and export a content plan; never render slides or select a style."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import content_plan as model
import export_content


def read_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def merge(base, patch):
    if not isinstance(patch, dict):
        raise model.PlanError('patch 顶层必须是对象；数组字段整组替换')
    result = deepcopy(base)
    for key, value in patch.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else deepcopy(value)
    return result


def content_hash(plan):
    return model.digest({k: v for k, v in plan.items() if k != 'reviews'})


def export(plan, output, draft=False):
    findings = model.lint(plan)
    if not draft:
        if any(s != 'confirmed' for s in model.review_status(plan).values()):
            raise model.PlanError('正式交付需要三轮有效用户确认；讨论用预览请加 --draft')
        if any(f['severity'] == 'error' for f in findings):
            raise model.PlanError('存在内容校验错误，不能交接设计')
    files = {'content_outline.md': export_content.markdown(plan, draft),
             'content_map.html': export_content.render_html(plan, draft),
             'content_plan.json': json_text(plan)}
    manifest = {'schema_version': model.VERSION, 'content_hash': content_hash(plan),
                'review_hash': model.digest(plan['reviews']), 'draft': draft,
                'ready_for_design': not draft, 'files': {}}
    for name, text in files.items():
        atomic_write(output / name, text)
        manifest['files'][name] = hashlib.sha256(text.encode()).hexdigest()
    atomic_write(output / 'content_manifest.json', json_text(manifest))
    return manifest


def check_export(plan, output):
    manifest = read_json(output / 'content_manifest.json')
    if manifest.get('content_hash') != content_hash(plan) or manifest.get('review_hash') != model.digest(plan['reviews']):
        raise model.PlanError('导出已过期：内容或确认状态已变化，请重新 export')
    expected = {'content_outline.md', 'content_map.html', 'content_plan.json'}
    if set(manifest.get('files', {})) != expected:
        raise model.PlanError('交付清单文件集合不完整')
    for name, checksum in manifest['files'].items():
        if hashlib.sha256((output / name).read_bytes()).hexdigest() != checksum:
            raise model.PlanError(f'导出文件已修改或损坏：{name}')
    return manifest


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', default=os.environ.get('PPTC_WORKSPACE', './ppt_workspace'))
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='保存第一轮草稿；不替用户确认')
    p.add_argument('--file', required=True)
    p = sub.add_parser('update', help='合并内容补丁，对象递归合并，数组整体替换')
    p.add_argument('--file', required=True)
    p = sub.add_parser('page', help='修改一页并使相关确认自动失效')
    p.add_argument('--id', required=True)
    p.add_argument('--patch', required=True)
    p = sub.add_parser('confirm', help='仅记录已发生的用户确认，禁止自动批准')
    p.add_argument('--stage', choices=model.STAGES, required=True)
    p.add_argument('--note', required=True, help='用户真实确认的原话或准确摘要')
    p = sub.add_parser('lint')
    p.add_argument('--stage', choices=model.STAGES, default='pages')
    sub.add_parser('status')
    sub.add_parser('sync', help='报告内容变化后的确认有效性')
    p = sub.add_parser('export', help='同时生成 Markdown、离线互动 HTML 和 JSON 交接件')
    p.add_argument('--draft', action='store_true')
    p.add_argument('--out', type=Path)
    p = sub.add_parser('check-export', help='检测导出过期或文件损坏')
    p.add_argument('--out', type=Path)
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    workspace = Path(args.workspace)
    path = workspace / 'plan.json'
    try:
        if args.command == 'init':
            if path.exists():
                raise model.PlanError(f'{path} 已存在，请用 update 或新的 workspace；不会覆盖原计划')
            raw = read_json(args.file)
            if not isinstance(raw, dict):
                raise model.PlanError('计划顶层必须是对象')
            raw['reviews'] = {}
            plan = model.normalize(raw)
            atomic_write(path, json_text(plan))
            print(f'已创建内容草稿：{path}；三轮确认均待用户完成')
            return 0
        plan = model.normalize(read_json(path))
        if args.command in {'update', 'page'}:
            patch = read_json(args.file if args.command == 'update' else args.patch)
            if not isinstance(patch, dict):
                raise model.PlanError('patch 必须是对象')
            if 'reviews' in patch:
                raise model.PlanError('不能通过内容补丁写入确认；请使用 confirm')
            if args.command == 'update':
                plan = merge(plan, patch)
            else:
                matches = [p for p in plan['pages'] if p['id'] == args.id]
                if not matches:
                    raise model.PlanError(f'找不到页面：{args.id}')
                if 'id' in patch and patch['id'] != args.id:
                    raise model.PlanError('page 补丁不能修改 id；使用 update 同步所有引用')
                matches[0].update(merge(matches[0], patch))
            plan = model.normalize(plan)
            atomic_write(path, json_text(plan))
            print(json_text(model.review_status(plan)), end='')
        elif args.command == 'confirm':
            plan = model.confirm(plan, args.stage, args.note)
            atomic_write(path, json_text(plan))
            print(f'已记录用户确认：{args.stage}；后续内容变更会使相应确认失效')
        elif args.command in {'status', 'sync'}:
            statuses = model.review_status(plan)
            print(json_text({'reviews': statuses, 'sections': len(plan['sections']),
                             'blocks': sum(len(s['blocks']) for s in plan['sections']),
                             'pages': len(plan['pages']),
                             'next': next((s for s in model.STAGES if statuses[s] != 'confirmed'), 'export / handoff')}), end='')
        elif args.command == 'lint':
            findings = model.lint(plan, args.stage)
            for finding in findings:
                print(f'[{finding["severity"]}] {finding["node"]}: {finding["message"]}')
            print(f'检查完成：{sum(f["severity"] == "error" for f in findings)} errors, '
                  f'{sum(f["severity"] == "warning" for f in findings)} warnings')
            return int(any(f['severity'] == 'error' for f in findings))
        elif args.command == 'export':
            output = args.out or workspace / 'output'
            export(plan, output, args.draft)
            print(f'已导出{"草稿" if args.draft else "已确认内容"}：{output.resolve()}')
        elif args.command == 'check-export':
            manifest = check_export(plan, args.out or workspace / 'output')
            print('导出与当前计划一致；' + ('草稿，不能交接设计' if manifest['draft'] else '内容已确认，可交接设计'))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'[plan_tool] {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
