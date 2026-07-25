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
    def test_v23_design_system_is_complete(self):
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
        self.assertEqual(len(compatibility["palettes"]), 11)
        self.assertEqual(len(compatibility["styles"]), 8)
        self.assertEqual(len(page_types["page_types"]), 11)
        self.assertEqual(len(industries["profiles"]), 4)

    def test_missing_semantic_token_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design"
            shutil.copytree(ROOT / "references" / "design", design)
            palette = design / "palettes" / "orange-teal.md"
            text = palette.read_text(encoding="utf-8")
            text = text.replace("| `{BACKGROUND}` |", "| `{BACKGROUND_REMOVED}` |", 1)
            palette.write_text(text, encoding="utf-8")

            errors = validate_design.validate(design)

            self.assertTrue(
                any("BACKGROUND" in error and "缺少语义 Token" in error for error in errors),
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


if __name__ == "__main__":
    unittest.main()
