import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INTAKE = SCRIPTS / "intake_visual_reference.py"
PREVIEW = SCRIPTS / "generate_palette_preview.py"


class VisualReferenceIntakeTests(unittest.TestCase):
    def make_image(self, path, color=(220, 225, 230)):
        Image.new("RGB", (1200, 675), color).save(path)

    def test_one_screenshot_stays_palette_or_layout_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "reference.png"
            output = tmp / "proposal.json"
            self.make_image(source)

            result = subprocess.run(
                [
                    sys.executable,
                    str(INTAKE),
                    "--source",
                    str(source),
                    "--source-url",
                    "https://example.com/reference",
                    "--liked",
                    "瓷白背景和单一蓝色聚焦",
                    "--scope",
                    "auto",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(proposal["classification"], "palette-or-layout")
            self.assertFalse(proposal["promotion_ready"])
            self.assertFalse(proposal["registry_mutation_allowed"])
            self.assertEqual(proposal["source_url"], "https://example.com/reference")
            self.assertEqual(proposal["liked"], ["瓷白背景和单一蓝色聚焦"])
            self.assertEqual(len(proposal["sources"]), 1)
            self.assertEqual(proposal["sources"][0]["width"], 1200)
            self.assertEqual(proposal["sources"][0]["height"], 675)
            self.assertEqual(
                proposal["sources"][0]["sha256"],
                hashlib.sha256(source.read_bytes()).hexdigest(),
            )
            self.assertFalse(proposal["sources"][0]["embedded"])

    def test_four_page_types_create_style_intake_without_auto_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            output = tmp / "proposal.json"
            command = [
                sys.executable,
                str(INTAKE),
                "--scope",
                "style",
                "--liked",
                "统一字体、材质和空间锚点",
                "--output",
                str(output),
            ]
            for index, page_type in enumerate(
                ("cover", "overview", "architecture", "detail"), 1
            ):
                source = tmp / f"{index}.png"
                self.make_image(source, color=(220 - index, 225, 230 + index))
                command.extend(["--source", str(source)])
                command.extend(["--page-type", page_type])

            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(proposal["classification"], "style-candidate")
            self.assertTrue(proposal["intake_complete"])
            self.assertFalse(proposal["promotion_ready"])
            self.assertIn(
                "cross-industry generality review",
                proposal["required_next_steps"],
            )
            self.assertIn(
                "neutral no-text no-brand reference generation",
                proposal["required_next_steps"],
            )


class PalettePreviewTests(unittest.TestCase):
    def test_porcelain_azure_preview_generator_outputs_three_neutral_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview"
            result = subprocess.run(
                [
                    sys.executable,
                    str(PREVIEW),
                    "--palette",
                    "porcelain-azure",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["palette"], "porcelain-azure")
            self.assertEqual(
                [item["role"] for item in manifest["assets"]],
                ["cover", "architecture", "detail"],
            )
            self.assertEqual(manifest["colors"]["BACKGROUND"], "#F6F4F0")
            self.assertEqual(manifest["colors"]["FOCUS"], "#1D6FD1")
            for item in manifest["assets"]:
                path = output / item["file"]
                with Image.open(path) as image:
                    self.assertEqual(image.format, "JPEG")
                    self.assertEqual(image.size, (1600, 900))
                    self.assertFalse(image.getexif())
                self.assertEqual(
                    item["sha256"],
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )

    def test_palette_preview_generator_has_no_text_rendering_path(self):
        source = PREVIEW.read_text(encoding="utf-8")

        self.assertNotIn("draw.text", source)
        self.assertNotIn("ImageFont", source)


if __name__ == "__main__":
    unittest.main()
