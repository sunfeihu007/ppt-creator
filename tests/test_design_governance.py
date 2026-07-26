import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import design_governance  # noqa: E402


def make_plan(palette="orange-teal", style="swiss-grid", hints=None):
    hints = hints or ["非对称封面", "横向分层架构", "主图加窄注释栏"]
    pages = []
    for index, hint in enumerate(hints, 1):
        pages.append(
            {
                "id": f"P{index:02d}",
                "template": "content",
                "page_type": "detail",
                "title": f"页面{index}",
                "points": [],
                "layout_hint": hint,
                "status": "pending",
                "prompt_file": f"prompts/P{index:02d}.txt",
                "image": f"pages/P{index:02d}.png",
            }
        )
    return {
        "topic": "视觉治理测试",
        "audience": "客户",
        "palette": palette,
        "style": style,
        "industry": "general",
        "provider": "codex",
        "image_transport": "native",
        "image_model": "gpt-image-2",
        "pages": pages,
    }


class DesignGovernanceTests(unittest.TestCase):
    def test_clean_core_plan_has_no_findings(self):
        findings = design_governance.lint_plan(make_plan())

        self.assertEqual(findings, [])

    def test_blocked_combination_is_an_error(self):
        findings = design_governance.lint_plan(
            make_plan(palette="swiss-ikb", style="glass-3d")
        )

        self.assertTrue(
            any(
                item["severity"] == "error"
                and item["code"] == "blocked-combination"
                for item in findings
            ),
            findings,
        )

    def test_specialized_and_legacy_choices_warn(self):
        specialized = design_governance.lint_plan(
            make_plan(palette="graphite-cobalt", style="glass-3d")
        )
        legacy = design_governance.lint_plan(
            make_plan(palette="tech-blue", style="lineart-minimal")
        )

        self.assertTrue(
            any(item["code"] == "specialized-combination" for item in specialized),
            specialized,
        )
        self.assertTrue(
            any(item["code"] == "legacy-combination" for item in legacy),
            legacy,
        )
        self.assertTrue(
            any(item["code"] == "legacy-palette" for item in legacy),
            legacy,
        )

    def test_three_consecutive_layouts_warn_with_page_ids(self):
        plan = make_plan(
            hints=["左图右文", "左右对分详解", "split image and text", "时间轴"]
        )

        findings = design_governance.lint_plan(plan)

        item = next(
            finding
            for finding in findings
            if finding["code"] == "repeated-layout-family"
        )
        self.assertEqual(item["pages"], ["P01", "P02", "P03"])
        self.assertIn("split", item["message"])

    def test_repeated_three_card_hints_warn(self):
        plan = make_plan(
            hints=["三等分卡片", "一个主系统", "three equal cards with icons"]
        )

        findings = design_governance.lint_plan(plan)

        item = next(
            finding
            for finding in findings
            if finding["code"] == "generic-card-repetition"
        )
        self.assertEqual(item["pages"], ["P01", "P03"])

    def test_cli_writes_json_and_strict_mode_fails_on_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            report_path = Path(tmp) / "report.json"
            plan_path.write_text(
                json.dumps(
                    make_plan(
                        hints=["左图右文", "左右对分详解", "split image and text"]
                    ),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "verify_design_plan.py"),
                    "--plan",
                    str(plan_path),
                    "--strict",
                    "--json",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(report["passed"])
            self.assertEqual(report["errors"], 0)
            self.assertGreaterEqual(report["warnings"], 1)


if __name__ == "__main__":
    unittest.main()
