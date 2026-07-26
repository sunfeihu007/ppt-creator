import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import plan_tool  # noqa: E402


def base_plan():
    return {
        "topic": "test",
        "audience": "team",
        "palette": None,
        "style": None,
        "provider": None,
        "review": {
            "max_confirmations": 3,
            "confirmations_used": 0,
            "checkpoints": [],
        },
        "phases": {phase: "pending" for phase in plan_tool.PHASES},
        "pages": [],
    }


class PlanToolImageConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        self.plan_path = self.workspace / "plan.json"
        self.patches = [
            mock.patch.object(plan_tool, "WS", str(self.workspace)),
            mock.patch.object(plan_tool, "PLAN", str(self.plan_path)),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.tmp.cleanup()

    def write_plan(self, plan):
        self.plan_path.write_text(
            json.dumps(plan, ensure_ascii=False), encoding="utf-8"
        )

    def read_plan(self):
        return json.loads(self.plan_path.read_text(encoding="utf-8"))

    def test_design_locks_provider_transport_and_model(self):
        self.write_plan(base_plan())
        args = argparse.Namespace(
            palette="orange-teal",
            style="glass-3d",
            industry="port-terminal",
            provider="agy",
            transport="native",
            model=None,
        )

        plan_tool.cmd_design(args)

        plan = self.read_plan()
        self.assertEqual(plan["provider"], "agy")
        self.assertEqual(plan["image_transport"], "native")
        self.assertEqual(
            plan["image_model"], "gemini-3.1-flash-image"
        )
        self.assertEqual(plan["industry"], "port-terminal")

    def test_legacy_design_lock_prints_reason_and_alternative(self):
        self.write_plan(base_plan())
        args = argparse.Namespace(
            palette="tech-blue",
            style="lineart-minimal",
            industry="general",
            provider="codex",
            transport="native",
            model=None,
        )

        with mock.patch("builtins.print") as print_mock:
            plan_tool.cmd_design(args)

        output = "\n".join(
            " ".join(str(part) for part in call.args)
            for call in print_mock.call_args_list
        )
        self.assertIn("legacy", output)
        self.assertIn("graphite-cobalt", output)

    def test_old_plan_defaults_visual_layers(self):
        plan = base_plan()
        plan["pages"] = [{
            "id": "P01",
            "template": "arch",
            "title": "架构",
            "status": "pending",
        }]
        self.write_plan(plan)

        loaded = plan_tool.load()

        self.assertEqual(loaded["industry"], "general")
        self.assertEqual(loaded["pages"][0]["page_type"], "architecture")

    def test_old_plan_defaults_project_contract_fields(self):
        plan = base_plan()
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "方案",
            "status": "pending",
        }]
        self.write_plan(plan)

        loaded = plan_tool.load()

        self.assertEqual(loaded["schema_version"], "2.4")
        self.assertEqual(loaded["assurance_profile"], "standard")
        self.assertEqual(loaded["delivery_mode"], "raster_slide")
        self.assertEqual(loaded["pages"][0]["source_refs"], [])

    def test_init_preserves_contract_and_page_references(self):
        draft_path = self.workspace / "draft.json"
        draft_path.write_text(
            json.dumps(
                {
                    "topic": "客户方案",
                    "audience": "客户",
                    "assurance_profile": "client-facing",
                    "requirements": [{
                        "id": "REQ-001",
                        "decision": "统一使用正式名称",
                        "affected_pages": ["P01"],
                    }],
                    "claim_constraints": [],
                    "source_registry": [],
                    "pages": [{
                        "id": "P01",
                        "template": "content",
                        "title": "总体方案",
                        "requirement_refs": ["REQ-001"],
                    }],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        plan_tool.cmd_init(argparse.Namespace(file=str(draft_path), force=False))

        initialized = self.read_plan()
        self.assertEqual(initialized["schema_version"], "2.4")
        self.assertEqual(initialized["assurance_profile"], "client-facing")
        self.assertEqual(
            initialized["pages"][0]["requirement_refs"], ["REQ-001"]
        )

    def test_unknown_industry_is_rejected(self):
        self.write_plan(base_plan())
        args = argparse.Namespace(
            palette="orange-teal",
            style="swiss-grid",
            industry="unknown-sector",
            provider="codex",
            transport="native",
            model=None,
        )

        with self.assertRaisesRegex(SystemExit, "未知行业视觉修饰"):
            plan_tool.cmd_design(args)

    def test_old_gemini_plan_without_metadata_still_loads(self):
        plan = base_plan()
        plan["provider"] = "gemini"
        self.write_plan(plan)

        loaded = plan_tool.load()

        self.assertEqual(loaded["image_transport"], "api")
        self.assertEqual(
            loaded["image_model"], "gemini-3.1-flash-image"
        )

    def test_old_codex_builtin_plan_is_canonicalized(self):
        plan = base_plan()
        plan["provider"] = "codex-builtin"
        self.write_plan(plan)

        loaded = plan_tool.load()

        self.assertEqual(loaded["provider"], "codex")
        self.assertEqual(loaded["image_transport"], "native")
        self.assertEqual(loaded["image_model"], "gpt-image-2")

    def test_old_codex_plan_without_transport_remains_cli(self):
        plan = base_plan()
        plan["provider"] = "codex"
        self.write_plan(plan)

        loaded = plan_tool.load()

        self.assertEqual(loaded["provider"], "codex")
        self.assertEqual(loaded["image_transport"], "cli")
        self.assertEqual(loaded["image_model"], "gpt-image-2")

    def test_invalid_provider_transport_combinations_fail(self):
        for provider, transport in (
            ("gemini", "native"),
            ("codex", "api"),
            ("agy", "api"),
        ):
            with self.subTest(provider=provider, transport=transport):
                with self.assertRaisesRegex(SystemExit, "不支持"):
                    plan_tool.resolve_image_config(
                        provider, transport=transport, model=None
                    )

    def test_provider_switch_records_all_metadata(self):
        plan = base_plan()
        plan.update({
            "provider": "gemini",
            "image_transport": "api",
            "image_model": "gemini-3.1-flash-image",
        })
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "方案",
            "status": "approved",
        }]
        self.write_plan(plan)
        loaded = plan_tool.load()
        plan_tool.save(loaded)
        args = argparse.Namespace(
            name="codex", transport="cli", model=None
        )

        plan_tool.cmd_provider(args)

        updated = self.read_plan()
        self.assertEqual(updated["provider"], "codex")
        self.assertEqual(updated["image_transport"], "cli")
        self.assertEqual(updated["image_model"], "gpt-image-2")
        self.assertEqual(updated["pages"][0]["status"], "pending")
        self.assertIn(
            "project_input_changed",
            updated["pages"][0]["dirty_reasons"],
        )

    def test_lint_command_fails_for_forbidden_term(self):
        plan = base_plan()
        plan["requirements"] = [{
            "id": "REQ-001",
            "decision": "不得使用旧名称",
            "forbidden_terms": ["Hermes"],
            "affected_pages": ["P01"],
        }]
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "Hermes 方案",
            "status": "pending",
        }]
        self.write_plan(plan)

        with self.assertRaisesRegex(SystemExit, "REQ-001"):
            plan_tool.cmd_lint(argparse.Namespace(ids="all"))

    def test_contract_command_invalidates_only_affected_page(self):
        plan = base_plan()
        plan["pages"] = [
            {
                "id": "P01",
                "template": "content",
                "title": "方案一",
                "status": "approved",
            },
            {
                "id": "P02",
                "template": "content",
                "title": "方案二",
                "status": "approved",
            },
        ]
        self.write_plan(plan)
        normalized = plan_tool.load()
        plan_tool.save(normalized)
        contract_path = self.workspace / "contract.json"
        contract_path.write_text(
            json.dumps({
                "requirements": [{
                    "id": "REQ-001",
                    "decision": "P01 使用批准名称",
                    "affected_pages": ["P01"],
                }]
            }, ensure_ascii=False),
            encoding="utf-8",
        )

        plan_tool.cmd_contract(argparse.Namespace(file=str(contract_path)))

        updated = self.read_plan()
        self.assertEqual(updated["pages"][0]["status"], "pending")
        self.assertEqual(updated["pages"][1]["status"], "approved")

    def test_page_patch_invalidates_modified_page(self):
        plan = base_plan()
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "旧标题",
            "status": "approved",
        }]
        self.write_plan(plan)
        normalized = plan_tool.load()
        plan_tool.save(normalized)
        patch_path = self.workspace / "page-patch.json"
        patch_path.write_text(
            json.dumps({"title": "新标题"}, ensure_ascii=False),
            encoding="utf-8",
        )

        plan_tool.cmd_page(
            argparse.Namespace(
                id="P01",
                status=None,
                image=None,
                notes=None,
                patch=str(patch_path),
            )
        )

        updated = self.read_plan()
        self.assertEqual(updated["pages"][0]["title"], "新标题")
        self.assertEqual(updated["pages"][0]["status"], "pending")

    def test_pages_generated_records_image_input_hash(self):
        plan = base_plan()
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "方案",
            "status": "prompted",
        }]
        self.write_plan(plan)

        plan_tool.cmd_pages(
            argparse.Namespace(ids="P01", status="generated")
        )

        updated = self.read_plan()
        self.assertEqual(updated["pages"][0]["status"], "generated")
        self.assertIsNotNone(
            updated["pages"][0]["image_input_hash"]
        )

    def test_sync_check_fails_after_manual_content_change(self):
        plan = base_plan()
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "旧标题",
            "status": "approved",
        }]
        self.write_plan(plan)
        normalized = plan_tool.load()
        plan_tool.save(normalized)
        manually_changed = self.read_plan()
        manually_changed["pages"][0]["title"] = "新标题"
        self.write_plan(manually_changed)

        with self.assertRaisesRegex(SystemExit, "STALE"):
            plan_tool.cmd_sync_check(argparse.Namespace())

    def test_reuse_command_sets_exact_asset_and_invalidates_alias(self):
        plan = base_plan()
        plan["pages"] = [
            {
                "id": "P01",
                "template": "content",
                "title": "导览",
                "status": "approved",
            },
            {
                "id": "P02",
                "template": "content",
                "title": "导览",
                "status": "approved",
            },
        ]
        self.write_plan(plan)
        normalized = plan_tool.load()
        plan_tool.save(normalized)

        plan_tool.cmd_reuse(
            argparse.Namespace(id="P02", source="P01")
        )

        updated = self.read_plan()
        self.assertEqual(updated["pages"][1]["reused_from"], "P01")
        self.assertEqual(updated["pages"][1]["reuse_mode"], "exact_asset")
        self.assertEqual(updated["pages"][1]["status"], "pending")

    def test_export_outline_writes_generated_plan_view(self):
        plan = base_plan()
        plan["topic"] = "方案"
        plan["pages"] = [{
            "id": "P01",
            "template": "content",
            "title": "总体方案",
            "points": ["统一协同"],
            "status": "pending",
        }]
        self.write_plan(plan)
        out = self.workspace / "final_outline.md"

        plan_tool.cmd_export_outline(argparse.Namespace(out=str(out)))

        text = out.read_text(encoding="utf-8")
        self.assertIn("# 方案", text)
        self.assertIn("### P01 总体方案", text)


if __name__ == "__main__":
    unittest.main()
