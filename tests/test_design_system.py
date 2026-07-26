from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_design  # noqa: E402


class DesignSystemValidationTests(unittest.TestCase):
    def test_v25_design_system_is_complete(self):
        design = ROOT / "references" / "design"
        errors = validate_design.validate(design)
        self.assertEqual(errors, [])
        compatibility = json.loads(
            (design / "compatibility.json").read_text(encoding="utf-8")
        )
        page_types = json.loads(
            (design / "page-types" / "index.json").read_text(encoding="utf-8")
        )
        industries = json.loads(
            (design / "industries" / "index.json").read_text(encoding="utf-8")
        )
        governance = json.loads(
            (design / "governance.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(compatibility["palettes"]), 12)
        self.assertEqual(len(compatibility["styles"]), 9)
        self.assertEqual(
            len(compatibility["palettes"]) * len(compatibility["styles"]),
            108,
        )
        self.assertEqual(
            set(governance["palette_profiles"]), set(compatibility["palettes"])
        )
        self.assertEqual(
            set(governance["style_profiles"]), set(compatibility["styles"])
        )
        self.assertEqual(len(page_types["page_types"]), 11)
        self.assertEqual(len(industries["profiles"]), 4)

    def test_missing_semantic_token_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            palette = design / "palettes" / "orange-teal.md"
            text = palette.read_text(encoding="utf-8")
            text = text.replace("| `{FOCUS_TEXT}` |", "| `{FOCUS_TEXT_REMOVED}` |", 1)
            palette.write_text(text, encoding="utf-8")

            errors = validate_design.validate(design)

            self.assertTrue(
                any("FOCUS_TEXT" in error and "缺少语义 Token" in error for error in errors),
                errors,
            )

    def test_low_contrast_text_role_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            palette = design / "palettes" / "orange-teal.md"
            text = palette.read_text(encoding="utf-8")
            marker = "| `{TEXT_PRIMARY}` | `#333333` | 深灰 | 标题与主要文字 |"
            self.assertIn(marker, text)
            text = text.replace(
                marker,
                marker
                + "\n| `{FOCUS_TEXT}` | `#FFFFFF` | 错误浅色 | 聚焦文字 |",
                1,
            )
            palette.write_text(text, encoding="utf-8")

            errors = validate_design.validate(design)

            self.assertTrue(
                any("FOCUS_TEXT" in error and "对比度" in error for error in errors),
                errors,
            )

    def test_material_conflicts_and_recommendation_budget_are_explicit(self):
        compatibility = json.loads(
            (
                ROOT / "references" / "design" / "compatibility.json"
            ).read_text(encoding="utf-8")
        )
        combinations = compatibility["combinations"]

        self.assertEqual(
            combinations["orange-teal"]["lineart-minimal"]["status"], "allowed"
        )
        self.assertEqual(
            combinations["tech-blue"]["lineart-minimal"]["status"], "legacy"
        )
        self.assertEqual(
            combinations["swiss-ikb"]["glass-3d"]["status"], "blocked"
        )
        self.assertEqual(
            combinations["finance-navy-teal"]["glass-3d"]["status"], "blocked"
        )
        for palette, row in combinations.items():
            recommended = [
                style
                for style, rule in row.items()
                if rule["status"] == "recommended"
            ]
            self.assertLessEqual(
                len(recommended),
                3,
                f"{palette} 推荐风格过多: {recommended}",
            )

    def test_missing_page_type_fragment_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            (design / "page-types" / "case.md").unlink()

            errors = validate_design.validate(design)

            self.assertTrue(
                any("page-types/case.md" in error for error in errors),
                errors,
            )

    def test_v25_release_contract_is_documented_and_evaluated(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        contract_ref = ROOT / "references" / "project-contract.md"
        evals = json.loads(
            (ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
        )["evals"]
        ids = [item["id"] for item in evals]
        prompts = "\n".join(item["prompt"] for item in evals)

        self.assertIn("v2.5.0", skill_text)
        self.assertIn("v2.5.0", readme_text)
        self.assertIn("references/project-contract.md", skill_text)
        self.assertIn("plan_tool.py sync-check", skill_text)
        self.assertIn("verify_semantics.py", skill_text)
        self.assertIn("verify_design_plan.py", skill_text)
        self.assertTrue(contract_ref.is_file())
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(range(19, 25)).issubset(ids))
        self.assertTrue(set(range(25, 33)).issubset(ids))
        for scenario in ("普通内部汇报", "金融案例", "制造", "港口"):
            self.assertIn(scenario, prompts)


if __name__ == "__main__":
    unittest.main()
