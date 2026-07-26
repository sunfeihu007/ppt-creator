import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import project_contract  # noqa: E402


def base_plan():
    return {
        "topic": "测试方案",
        "audience": "客户",
        "palette": "orange-teal",
        "style": "swiss-grid",
        "industry": "general",
        "provider": "codex",
        "image_transport": "native",
        "image_model": "gpt-image-2",
        "pages": [
            {
                "id": "P01",
                "template": "content",
                "page_type": "detail",
                "title": "总体方案",
                "subtitle": "",
                "points": ["统一协同"],
                "layout_hint": "",
                "notes": "【普通页】3-4分钟",
                "status": "pending",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
            },
            {
                "id": "P02",
                "template": "case",
                "page_type": "case",
                "title": "客户案例",
                "subtitle": "",
                "points": ["方案示例"],
                "layout_hint": "",
                "notes": "【普通页】3-4分钟",
                "status": "pending",
                "prompt_file": "prompts/P02.txt",
                "image": "pages/P02.png",
            },
        ],
    }


class ContractSchemaTests(unittest.TestCase):
    def test_legacy_plan_is_normalized_without_losing_existing_fields(self):
        plan = base_plan()
        plan["custom_field"] = {"keep": True}

        normalized = project_contract.normalize_plan(plan)

        self.assertEqual(normalized["schema_version"], "2.4")
        self.assertEqual(normalized["assurance_profile"], "standard")
        self.assertEqual(normalized["delivery_mode"], "raster_slide")
        self.assertEqual(normalized["requirements"], [])
        self.assertEqual(normalized["claim_constraints"], [])
        self.assertEqual(normalized["source_registry"], [])
        self.assertEqual(normalized["custom_field"], {"keep": True})
        page = normalized["pages"][0]
        self.assertEqual(page["requirement_refs"], [])
        self.assertEqual(page["claim_refs"], [])
        self.assertEqual(page["source_refs"], [])
        self.assertEqual(page["asset_provenance"], [])
        self.assertIsNone(page["evidence_level"])
        self.assertEqual(page["provenance_label"], "")
        self.assertIsNone(page["reused_from"])
        self.assertIsNone(page["reuse_mode"])
        self.assertEqual(page["dirty_reasons"], [])
        self.assertIsNone(page["prompt_input_hash"])
        self.assertIsNone(page["image_input_hash"])

    def test_invalid_assurance_profile_is_rejected(self):
        plan = base_plan()
        plan["assurance_profile"] = "maximum"

        with self.assertRaisesRegex(project_contract.ContractError, "assurance_profile"):
            project_contract.normalize_plan(plan)

    def test_unsupported_delivery_mode_is_rejected(self):
        plan = base_plan()
        plan["delivery_mode"] = "editable_native"

        with self.assertRaisesRegex(project_contract.ContractError, "delivery_mode"):
            project_contract.normalize_plan(plan)

    def test_duplicate_contract_ids_are_rejected_across_collections(self):
        plan = base_plan()
        plan["requirements"] = [{"id": "RULE-001", "decision": "使用批准名称"}]
        plan["claim_constraints"] = [{"id": "RULE-001", "rule": "不得夸大"}]

        with self.assertRaisesRegex(project_contract.ContractError, "重复"):
            project_contract.normalize_plan(plan)

    def test_missing_rule_and_source_references_are_rejected(self):
        plan = base_plan()
        plan["pages"][0]["requirement_refs"] = ["REQ-MISSING"]
        plan["pages"][0]["source_refs"] = ["SRC-MISSING"]

        with self.assertRaisesRegex(project_contract.ContractError, "REQ-MISSING"):
            project_contract.normalize_plan(plan)

    def test_missing_reuse_source_is_rejected(self):
        plan = base_plan()
        plan["pages"][1]["reused_from"] = "P99"
        plan["pages"][1]["reuse_mode"] = "exact_asset"

        with self.assertRaisesRegex(project_contract.ContractError, "P99"):
            project_contract.normalize_plan(plan)

    def test_self_reuse_is_rejected(self):
        plan = base_plan()
        plan["pages"][0]["reused_from"] = "P01"
        plan["pages"][0]["reuse_mode"] = "exact_asset"

        with self.assertRaisesRegex(project_contract.ContractError, "自身"):
            project_contract.normalize_plan(plan)

    def test_reuse_cycle_is_rejected(self):
        plan = base_plan()
        plan["pages"][0].update(
            {"reused_from": "P02", "reuse_mode": "exact_asset"}
        )
        plan["pages"][1].update(
            {"reused_from": "P01", "reuse_mode": "exact_asset"}
        )

        with self.assertRaisesRegex(project_contract.ContractError, "循环"):
            project_contract.normalize_plan(plan)

    def test_normalization_does_not_share_mutable_defaults_between_pages(self):
        plan = project_contract.normalize_plan(copy.deepcopy(base_plan()))

        plan["pages"][0]["source_refs"].append("SRC-LOCAL")

        self.assertEqual(plan["pages"][1]["source_refs"], [])


def finding_keys(findings):
    return {
        (item["severity"], item["page"], item["rule_id"])
        for item in findings
    }


class SemanticLintTests(unittest.TestCase):
    def test_required_term_only_applies_to_affected_pages(self):
        plan = base_plan()
        plan["requirements"] = [{
            "id": "REQ-001",
            "decision": "平台名称统一为 Harness",
            "required_terms": ["Harness"],
            "affected_pages": ["P01"],
        }]
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(("error", "P01", "REQ-001"), finding_keys(findings))
        self.assertNotIn(("error", "P02", "REQ-001"), finding_keys(findings))

    def test_forbidden_term_is_an_error(self):
        plan = base_plan()
        plan["pages"][0]["points"] = ["Hermes 负责任务协同"]
        plan["requirements"] = [{
            "id": "REQ-001",
            "decision": "不得使用旧名称",
            "forbidden_terms": ["Hermes"],
            "affected_pages": ["P01"],
        }]
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(("error", "P01", "REQ-001"), finding_keys(findings))
        self.assertIn("Hermes", findings[0]["message"])

    def test_claim_constraint_uses_the_same_exact_checks(self):
        plan = base_plan()
        plan["pages"][0]["points"] = ["最终由审批岗位完成"]
        plan["claim_constraints"] = [{
            "id": "CLAIM-001",
            "rule": "不得擅自指定客户审批责任",
            "forbidden_terms": ["最终由审批岗位完成"],
            "affected_pages": ["P01"],
        }]
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(("error", "P01", "CLAIM-001"), finding_keys(findings))

    def test_client_facing_case_without_evidence_metadata_warns(self):
        plan = base_plan()
        plan["assurance_profile"] = "client-facing"
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(
            ("warning", "P02", "ASSURANCE-EVIDENCE"),
            finding_keys(findings),
        )

    def test_evidence_sensitive_verified_case_requires_source(self):
        plan = base_plan()
        plan["assurance_profile"] = "evidence-sensitive"
        plan["pages"][1]["evidence_level"] = "verified"
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(
            ("error", "P02", "ASSURANCE-SOURCE"),
            finding_keys(findings),
        )

    def test_evidence_sensitive_conceptual_case_requires_visible_label(self):
        plan = base_plan()
        plan["assurance_profile"] = "evidence-sensitive"
        plan["pages"][1]["evidence_level"] = "conceptual"
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(plan)

        self.assertIn(
            ("error", "P02", "ASSURANCE-PROVENANCE"),
            finding_keys(findings),
        )

        plan["pages"][1]["provenance_label"] = "方案示意"
        findings = project_contract.lint_pages(plan)
        self.assertNotIn(
            ("error", "P02", "ASSURANCE-PROVENANCE"),
            finding_keys(findings),
        )

    def test_text_override_allows_ocr_text_to_be_checked(self):
        plan = base_plan()
        plan["requirements"] = [{
            "id": "REQ-001",
            "decision": "不得使用旧名称",
            "forbidden_terms": ["Hermes"],
            "affected_pages": ["P01"],
        }]
        plan = project_contract.normalize_plan(plan)

        findings = project_contract.lint_pages(
            plan, text_overrides={"P01": "页面 OCR 识别到 Hermes"}
        )

        self.assertIn(("error", "P01", "REQ-001"), finding_keys(findings))


class ContractHashTests(unittest.TestCase):
    def approved_plan_with_hashes(self):
        plan = project_contract.normalize_plan(base_plan())
        for page in plan["pages"]:
            page["status"] = "approved"
            project_contract.record_prompt_hash(plan, page)
            project_contract.record_image_hash(plan, page)
        return plan

    def test_hash_is_stable_for_equivalent_dictionary_order(self):
        first = {"b": 2, "a": {"d": 4, "c": 3}}
        second = {"a": {"c": 3, "d": 4}, "b": 2}

        self.assertEqual(
            project_contract.stable_hash(first),
            project_contract.stable_hash(second),
        )

    def test_requirement_change_invalidates_only_affected_page(self):
        plan = self.approved_plan_with_hashes()
        original_p02_hash = plan["pages"][1]["image_input_hash"]
        plan["requirements"] = [{
            "id": "REQ-001",
            "decision": "平台名称统一为 Harness",
            "affected_pages": ["P01"],
        }]

        changed = project_contract.invalidate_stale_pages(plan)

        self.assertEqual(changed, ["P01"])
        self.assertEqual(plan["pages"][0]["status"], "pending")
        self.assertIn(
            "project_input_changed", plan["pages"][0]["dirty_reasons"]
        )
        self.assertIsNone(plan["pages"][0]["prompt_input_hash"])
        self.assertIsNone(plan["pages"][0]["image_input_hash"])
        self.assertEqual(plan["pages"][1]["status"], "approved")
        self.assertEqual(
            plan["pages"][1]["image_input_hash"], original_p02_hash
        )

    def test_global_design_change_invalidates_every_generated_page(self):
        plan = self.approved_plan_with_hashes()
        plan["style"] = "flat-editorial"

        changed = project_contract.invalidate_stale_pages(plan)

        self.assertEqual(changed, ["P01", "P02"])
        self.assertTrue(
            all(page["status"] == "pending" for page in plan["pages"])
        )

    def test_referenced_source_change_invalidates_only_consumer(self):
        plan = base_plan()
        plan["source_registry"] = [{
            "id": "SRC-001",
            "type": "file",
            "label": "客户材料",
            "path": "source-v1.pdf",
        }]
        plan["pages"][0]["source_refs"] = ["SRC-001"]
        plan = project_contract.normalize_plan(plan)
        for page in plan["pages"]:
            page["status"] = "approved"
            project_contract.record_prompt_hash(plan, page)
            project_contract.record_image_hash(plan, page)
        plan["source_registry"][0]["path"] = "source-v2.pdf"

        changed = project_contract.invalidate_stale_pages(plan)

        self.assertEqual(changed, ["P01"])
        self.assertEqual(plan["pages"][1]["status"], "approved")

    def test_legacy_approved_page_adopts_current_hashes(self):
        plan = base_plan()
        plan["pages"][0]["status"] = "approved"

        normalized = project_contract.normalize_plan(plan)

        self.assertIsNotNone(normalized["pages"][0]["prompt_input_hash"])
        self.assertIsNotNone(normalized["pages"][0]["image_input_hash"])
        self.assertEqual(normalized["pages"][0]["dirty_reasons"], [])

    def test_sync_findings_report_modified_approved_page(self):
        plan = self.approved_plan_with_hashes()
        plan["pages"][0]["title"] = "已修改标题"

        findings = project_contract.sync_findings(plan)

        self.assertTrue(
            any(
                item["page"] == "P01"
                and item["reason"] == "project_input_changed"
                for item in findings
            )
        )

    def test_source_change_invalidates_exact_reuse_descendant(self):
        plan = base_plan()
        plan["pages"][1].update(
            {
                "title": "总体方案",
                "points": ["统一协同"],
                "reused_from": "P01",
                "reuse_mode": "exact_asset",
            }
        )
        plan = project_contract.normalize_plan(plan)
        for page in plan["pages"]:
            page["status"] = "approved"
            project_contract.record_prompt_hash(plan, page)
            project_contract.record_image_hash(plan, page)
        plan["pages"][0]["title"] = "更新后的总体方案"

        changed = project_contract.invalidate_stale_pages(plan)

        self.assertEqual(changed, ["P01", "P02"])


class ContractOutputTests(unittest.TestCase):
    def test_effective_image_resolves_exact_reuse_source(self):
        plan = base_plan()
        plan["pages"][1].update(
            {"reused_from": "P01", "reuse_mode": "exact_asset"}
        )
        plan = project_contract.normalize_plan(plan)

        self.assertEqual(
            project_contract.effective_image(plan, "P02"),
            "pages/P01.png",
        )
        self.assertEqual(
            project_contract.effective_page(plan, "P02")["id"],
            "P01",
        )

    def test_render_outline_is_a_deterministic_plan_view(self):
        plan = project_contract.normalize_plan(base_plan())
        expected = (
            "<!-- Generated by PPT Creator v2.4; do not edit. -->\n"
            "# 测试方案\n\n"
            "- 受众：客户\n"
            "- 保障级别：standard\n"
            "- 交付模式：raster_slide\n\n"
            "## 逐页大纲\n\n"
            "### P01 总体方案\n\n"
            "- 统一协同\n\n"
            "### P02 客户案例\n\n"
            "- 方案示例\n"
        )

        self.assertEqual(project_contract.render_outline(plan), expected)


if __name__ == "__main__":
    unittest.main()
