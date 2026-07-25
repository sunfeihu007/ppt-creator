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
        self.write_plan(plan)
        args = argparse.Namespace(
            name="codex", transport="cli", model=None
        )

        plan_tool.cmd_provider(args)

        updated = self.read_plan()
        self.assertEqual(updated["provider"], "codex")
        self.assertEqual(updated["image_transport"], "cli")
        self.assertEqual(updated["image_model"], "gpt-image-2")


if __name__ == "__main__":
    unittest.main()
