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


if __name__ == "__main__":
    unittest.main()
