import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import content_plan as model
import export_content
import plan_tool


def example():
    return model.normalize(json.loads((ROOT / 'examples/content-plan.json').read_text()))


def approved():
    plan = example()
    for stage in model.STAGES:
        plan = model.confirm(plan, stage, '测试中的模拟用户确认')
    return plan


class ContentModelTests(unittest.TestCase):
    def test_example_has_complete_hierarchy_and_no_findings(self):
        plan = example()
        self.assertEqual(model.lint(plan), [])
        self.assertEqual(len(model.nodes(plan)), 14)
        self.assertEqual(len(plan['pages']), 6)

    def test_initial_draft_accepts_empty_lower_layers(self):
        plan = example()
        plan['pages'] = []
        for section in plan['sections']:
            section['blocks'] = []
        plan['relations'] = plan['relations'][:2]
        plan = model.normalize(plan)
        self.assertEqual(model.lint(plan, 'outline'), [])
        self.assertTrue(model.lint(plan, 'content'))
        self.assertTrue(model.lint(plan, 'pages'))

    def test_does_not_mutate_input(self):
        raw = {'deck': {'title': '草稿'}}
        model.normalize(raw)
        self.assertEqual(raw, {'deck': {'title': '草稿'}})

    def test_legacy_plans_are_not_silently_promoted(self):
        with self.assertRaisesRegex(model.PlanError, '旧计划'):
            model.normalize({'schema_version': '2.4', 'topic': 'old', 'pages': []})

    def test_legacy_visual_fields_are_rejected(self):
        for level in ('deck', 'page', 'root'):
            plan = example()
            target = {'deck': plan['deck'], 'page': plan['pages'][0], 'root': plan}[level]
            target['palette'] = 'old-palette'
            with self.subTest(level=level), self.assertRaises(model.PlanError):
                model.normalize(plan)

    def test_duplicate_and_missing_ids_are_rejected(self):
        for change in ('duplicate', 'missing_parent', 'bad_relation'):
            plan = example()
            if change == 'duplicate':
                plan['pages'][0]['id'] = 'S1'
            elif change == 'missing_parent':
                plan['pages'][0]['block_id'] = 'B-missing'
            else:
                plan['relations'][0]['to'] = 'missing'
            with self.subTest(change=change), self.assertRaises(model.PlanError):
                model.normalize(plan)

    def test_bad_relation_and_duplicate_edges_rejected(self):
        for change in ('type', 'self', 'duplicate', 'reason'):
            plan = example()
            if change == 'type':
                plan['relations'][0]['type'] = 'vague'
            elif change == 'self':
                plan['relations'][0]['to'] = 'S1'
            elif change == 'reason':
                plan['relations'][0]['reason'] = ' '
            else:
                plan['relations'].append(copy.deepcopy(plan['relations'][0]))
            with self.subTest(change=change), self.assertRaises(model.PlanError):
                model.normalize(plan)

    def test_disconnected_sections_and_blocks_block_confirmation(self):
        plan = example()
        plan['relations'] = []
        findings = model.lint(plan)
        self.assertTrue(any(f['node'] == 'DECK' and '未连通' in f['message'] for f in findings))
        self.assertTrue(any(f['node'] == 'S2' and '未连通' in f['message'] for f in findings))

    def test_focus_role_and_thesis_are_required(self):
        plan = example()
        for field in ('focus', 'role_in_deck', 'thesis', 'role_in_parent'):
            plan['pages'][0].pop(field)
        missing = ' '.join(f['message'] for f in model.lint(plan))
        for field in ('focus', 'role_in_deck', 'thesis', 'role_in_parent'):
            self.assertIn(field, missing)

    def test_page_distribution_and_transitions_are_checked(self):
        plan = example()
        plan['pages'][3]['block_id'] = 'B2'
        plan['pages'][0].pop('transition')
        messages = ' '.join(f['message'] for f in model.lint(plan))
        self.assertIn('尚未分配页面', messages)
        self.assertIn('transition', messages)

    def test_reading_order_covers_entities_exactly(self):
        plan = example()
        plan['pages'][0]['information_structure']['reading_order'] = ['E1', 'E1']
        with self.assertRaisesRegex(model.PlanError, 'reading_order'):
            model.normalize(plan)

    def test_entity_relationships_and_comparison_dimensions_required(self):
        plan = example()
        plan['pages'][0]['information_structure']['relations'] = []
        plan['pages'][1]['information_structure']['dimensions'] = []
        messages = ' '.join(f['message'] for f in model.lint(plan))
        self.assertIn('未说明的关系', messages)
        self.assertIn('比较维度', messages)

    def test_nonfinite_or_negative_time_rejected(self):
        for value in (True, -1, 0, float('nan'), float('inf'), '3'):
            plan = example()
            plan['pages'][0]['minutes'] = value
            with self.subTest(value=value), self.assertRaises(model.PlanError):
                model.normalize(plan)

    def test_time_mismatch_is_a_warning_not_fake_pass(self):
        plan = example()
        plan['deck']['duration_minutes'] = 60
        findings = model.lint(plan)
        self.assertTrue(any(f['severity'] == 'warning' and '时长' in f['message'] for f in findings))


class EvidenceTests(unittest.TestCase):
    def test_verified_claim_requires_source(self):
        plan = example()
        plan['pages'][0]['evidence'] = [{'claim': '已实现', 'status': 'verified', 'source_refs': []}]
        self.assertTrue(any('必须引用来源' in f['message'] for f in model.lint(plan)))

    def test_unknown_source_is_rejected(self):
        plan = example()
        plan['pages'][0]['evidence'][0]['source_refs'] = ['MISSING']
        with self.assertRaisesRegex(model.PlanError, '不存在的来源'):
            model.normalize(plan)

    def test_hypothesis_requires_boundary(self):
        plan = example()
        plan['pages'][0]['evidence'][0]['note'] = ''
        self.assertTrue(any('假设' in f['message'] for f in model.lint(plan)))

    def test_sensitive_claim_blocks_while_normal_claim_warns(self):
        plan = example()
        plan['pages'][0]['evidence'][0]['status'] = 'needs_source'
        for profile, severity in [('standard', 'warning'), ('client-facing', 'warning'), ('evidence-sensitive', 'error')]:
            plan['assurance_profile'] = profile
            findings = model.lint(plan)
            self.assertTrue(any(f['severity'] == severity and '待补充来源' in f['message'] for f in findings))

    def test_scoped_terms_apply_to_subtree_without_leaking_to_other_pages(self):
        plan = example()
        plan['requirements'] = [{'id': 'R', 'text': '术语约束', 'applies_to': ['B2'],
                                 'required_terms': ['交接条件'], 'forbidden_terms': ['异常触发条件']}]
        self.assertEqual(model.lint(plan), [])
        plan['requirements'][0]['applies_to'] = ['S2']
        self.assertTrue(any('禁止词' in f['message'] for f in model.lint(plan)))

    def test_questions_only_block_their_stage_and_downstream(self):
        plan = example()
        plan['open_questions'] = [{'question': '数据口径待确认', 'stage': 'pages', 'blocking': True}]
        self.assertEqual(model.lint(plan, 'outline'), [])
        self.assertEqual(model.lint(plan, 'content'), [])
        self.assertTrue(any('数据口径' in f['message'] for f in model.lint(plan)))


class ReviewTests(unittest.TestCase):
    def test_confirmations_are_sequential_and_cannot_skip(self):
        with self.assertRaisesRegex(model.PlanError, 'outline'):
            model.confirm(example(), 'pages', '模拟确认')

    def test_incomplete_stage_cannot_be_confirmed(self):
        plan = example()
        plan['deck']['thesis'] = ''
        with self.assertRaisesRegex(model.PlanError, 'thesis'):
            model.confirm(plan, 'outline', '模拟确认')

    def test_page_changes_preserve_outline_and_content_confirmation(self):
        plan = approved()
        plan['pages'][0]['focus'] = '调整后的重点'
        self.assertEqual(model.review_status(plan), {'outline': 'confirmed', 'content': 'confirmed', 'pages': 'stale'})

    def test_block_changes_invalidate_content_and_pages(self):
        plan = approved()
        plan['sections'][0]['blocks'][0]['thesis'] = '修改小块主旨'
        self.assertEqual(model.review_status(plan), {'outline': 'confirmed', 'content': 'stale', 'pages': 'stale'})

    def test_deck_changes_invalidate_all_confirmations(self):
        plan = approved()
        plan['deck']['objective'] = '新的沟通目标'
        self.assertTrue(all(s == 'stale' for s in model.review_status(plan).values()))

    def test_relationship_changes_invalidate_their_content_level(self):
        plan = approved()
        plan['relations'][-1]['reason'] = '新的逐页逻辑解释'
        self.assertEqual(model.review_status(plan)['content'], 'confirmed')
        self.assertEqual(model.review_status(plan)['pages'], 'stale')

    def test_source_edits_invalidate_content_and_downstream(self):
        plan = approved()
        plan['sources'][0]['locator'] = 'changed.md'
        self.assertEqual(model.review_status(plan)['outline'], 'confirmed')
        self.assertEqual(model.review_status(plan)['content'], 'stale')
        self.assertEqual(model.review_status(plan)['pages'], 'stale')


class ExportTests(unittest.TestCase):
    def test_draft_exports_all_content_and_interactive_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            plan_tool.export(example(), output, draft=True)
            self.assertEqual(len(list(output.iterdir())), 4)
            outline = (output / 'content_outline.md').read_text()
            for term in ('不可进入版式设计', '大块与小块内容', '逻辑关系', '在整套 PPT 中的作用', '信息实体', '承接下一页'):
                self.assertIn(term, outline)
            page = (output / 'content_map.html').read_text()
            self.assertIn('renderGraph', page)
            self.assertNotIn('src="https://', page)
            self.assertTrue(plan_tool.check_export(example(), output)['draft'])

    def test_formal_export_requires_confirmations(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(model.PlanError, '三轮'):
            plan_tool.export(example(), Path(tmp))

    def test_approved_export_then_content_or_review_change_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, output = approved(), Path(tmp)
            plan_tool.export(plan, output)
            self.assertTrue(plan_tool.check_export(plan, output)['ready_for_design'])
            plan['reviews']['pages']['note'] = '不同的用户确认依据'
            with self.assertRaisesRegex(model.PlanError, '已过期'):
                plan_tool.check_export(plan, output)

    def test_output_tampering_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, output = example(), Path(tmp)
            plan_tool.export(plan, output, True)
            (output / 'content_map.html').write_text('changed')
            with self.assertRaisesRegex(model.PlanError, '已修改或损坏'):
                plan_tool.check_export(plan, output)

    def test_untrusted_content_cannot_break_out_of_data_script(self):
        plan = example()
        payload = '</script><script>window.PWNED=true</script><img src=x onerror=alert(1)>'
        plan['pages'][0]['title'] = payload
        rendered = export_content.render_html(plan, True)
        self.assertNotIn(payload, rendered)
        self.assertIn('\\u003c/script\\u003e', rendered)
        self.assertEqual(rendered.count('<script'), 2)

    def test_html_draft_handles_incomplete_information_structure(self):
        plan = example()
        plan['pages'][0]['information_structure'] = {'kind': 'list'}
        normalized = model.normalize(plan)
        self.assertEqual(normalized['pages'][0]['information_structure']['entities'], [])
        self.assertIn('"entities": []', export_content.render_html(normalized, True))

    def test_page_array_order_is_preserved_in_outline(self):
        plan = example()
        plan['pages'][0], plan['pages'][1] = plan['pages'][1], plan['pages'][0]
        outline = export_content.markdown(plan, True)
        self.assertLess(outline.index('### 01 / P02'), outline.index('### 02 / P01'))


class CliTests(unittest.TestCase):
    def test_full_review_export_and_revision_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            def run(*args):
                return subprocess.run([sys.executable, str(ROOT / 'scripts/plan_tool.py'), '--workspace', tmp, *args],
                                      text=True, capture_output=True, cwd=ROOT)
            result = run('init', '--file', str(ROOT / 'examples/content-plan.json'))
            self.assertEqual(result.returncode, 0, result.stderr)
            original = (workspace / 'plan.json').read_bytes()
            self.assertNotEqual(run('init', '--file', str(ROOT / 'examples/content-plan.json')).returncode, 0)
            self.assertEqual((workspace / 'plan.json').read_bytes(), original)
            self.assertNotEqual(run('export').returncode, 0)
            self.assertEqual(run('export', '--draft').returncode, 0)
            for stage in model.STAGES:
                result = run('confirm', '--stage', stage, '--note', '测试模拟用户确认')
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(run('export').returncode, 0)
            self.assertEqual(run('check-export').returncode, 0)
            patch = workspace / 'patch.json'
            patch.write_text(json.dumps({'focus': '新的内容重点'}))
            self.assertEqual(run('page', '--id', 'P01', '--patch', str(patch)).returncode, 0)
            status = json.loads(run('status').stdout)['reviews']
            self.assertEqual(status, {'outline': 'confirmed', 'content': 'confirmed', 'pages': 'stale'})
            self.assertNotEqual(run('check-export').returncode, 0)
            self.assertNotEqual(run('export').returncode, 0)
            patch.write_text('{"reviews": {}}')
            self.assertNotEqual(run('update', '--file', str(patch)).returncode, 0)
            patch.write_text('{"block_id": "missing"}')
            before = (workspace / 'plan.json').read_bytes()
            self.assertNotEqual(run('page', '--id', 'P01', '--patch', str(patch)).returncode, 0)
            self.assertEqual((workspace / 'plan.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
