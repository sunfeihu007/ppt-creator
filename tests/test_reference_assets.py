import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "references" / "design"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_style_refs  # noqa: E402


class ReferenceAssetTests(unittest.TestCase):
    def test_generated_reference_manifest_and_files_are_valid(self):
        errors = generate_style_refs.validate_assets(DESIGN)

        self.assertEqual(errors, [])
        manifest = json.loads(
            (DESIGN / "reference-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(manifest["assets"]), 21)
        self.assertEqual(
            manifest["rules"],
            {
                "text_free": True,
                "brand_free": True,
                "data_free": True,
                "palette_neutral": True,
            },
        )
        self.assertEqual(
            {asset["width"] for asset in manifest["assets"]}, {1600}
        )
        self.assertEqual(
            {asset["height"] for asset in manifest["assets"]}, {900}
        )

    def test_generator_contains_no_text_rendering_path(self):
        source = (SCRIPTS / "generate_style_refs.py").read_text(
            encoding="utf-8"
        )

        self.assertIsNone(re.search(r"\bdraw\.text(?:length|bbox)?\s*\(", source))
        self.assertNotIn("ImageFont", source)


if __name__ == "__main__":
    unittest.main()
