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

    def test_invalid_alternative_target_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            compatibility_path = design / "compatibility.json"
            compatibility = json.loads(
                compatibility_path.read_text(encoding="utf-8")
            )
            compatibility["combinations"]["orange-teal"]["hud-frame"][
                "alternatives"
            ] = ["missing-palette × swiss-grid"]
            compatibility_path.write_text(
                json.dumps(compatibility, ensure_ascii=False),
                encoding="utf-8",
            )

            errors = validate_design.validate(design)

            self.assertTrue(
                any("替代组合" in error and "未登记" in error for error in errors),
                errors,
            )

    def test_invalid_global_micro_label_budget_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            governance_path = design / "governance.json"
            governance = json.loads(
                governance_path.read_text(encoding="utf-8")
            )
            governance["deck_rules"]["max_micro_labels_per_page"] = 0
            governance_path.write_text(
                json.dumps(governance, ensure_ascii=False),
                encoding="utf-8",
            )

            errors = validate_design.validate(design)

            self.assertTrue(
                any("max_micro_labels_per_page" in error for error in errors),
                errors,
            )

    def test_prompt_guidance_contains_no_client_or_obsolete_default_fixture(self):
        prompt_guidance = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(
                (ROOT / "references" / "design" / "styles").glob("*.md")
            )
            + sorted(
                (ROOT / "references" / "design" / "palettes").glob("*.md")
            )
        )
        forbidden = (
            "奇瑞商用车",
            "宁波航交所",
            "联通知识管理平台",
            "联通新一代知识管理平台",
            "兴业银行审计智能体",
            "明东码头",
            "宁波外理",
            "外一知识中台",
            "智能理货审核系统",
            "ACCURACY: 99.9%",
            "三个并排玻璃圆角卡片",
            "三个白色圆角卡片横排",
            "三组横排：大号细线描图标",
            "屏幕为浅灰占位",
        )

        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, prompt_guidance)

    def test_reference_manifest_integrity_is_part_of_design_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            manifest_path = design / "reference-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0]["sha256"] = "0" * 64
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )

            errors = validate_design.validate(design)

            self.assertTrue(
                any("sha256" in error for error in errors),
                errors,
            )

    def test_malformed_reference_manifest_entry_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            manifest_path = design / "reference-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0] = "not-an-object"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )

            errors = validate_design.validate(design)

            self.assertTrue(
                any("manifest 资产条目必须是对象" in error for error in errors),
                errors,
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
