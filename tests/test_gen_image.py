import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gen_image  # noqa: E402


class ProviderResolutionTests(unittest.TestCase):
    def test_auto_uses_locked_script_transport(self):
        plan = {"provider": "gemini", "image_transport": "api"}
        self.assertEqual(
            gen_image.resolve_provider("auto", None, plan),
            ("gemini", "api"),
        )

    def test_auto_rejects_agy_native_lock_in_script(self):
        plan = {"provider": "agy", "image_transport": "native"}
        with self.assertRaisesRegex(RuntimeError, "generate_image"):
            gen_image.resolve_provider("auto", None, plan)

    def test_auto_rejects_codex_native_lock_in_script(self):
        plan = {"provider": "codex", "image_transport": "native"}
        with self.assertRaisesRegex(RuntimeError, "image_gen"):
            gen_image.resolve_provider("auto", None, plan)

    def test_explicit_provider_cannot_override_lock(self):
        plan = {"provider": "codex", "image_transport": "native"}
        with self.assertRaisesRegex(RuntimeError, "plan_tool.py provider"):
            gen_image.resolve_provider("gemini", "api", plan)

    def test_both_is_rejected_after_provider_lock(self):
        with self.assertRaisesRegex(RuntimeError, "锁定"):
            gen_image.resolve_provider(
                "both", None, {"provider": "gemini", "image_transport": "api"}
            )

    def test_unlocked_auto_uses_other_client_default(self):
        with mock.patch(
            "gen_image.image_providers.detect_script_provider",
            return_value="gemini",
        ):
            self.assertEqual(
                gen_image.resolve_provider("auto", None, {}),
                ("gemini", "api"),
            )

    def test_locked_gemini_model_cannot_be_overridden_by_environment(self):
        plan = {
            "provider": "gemini",
            "image_transport": "api",
            "image_model": "gemini-3.1-flash-image",
        }
        with mock.patch.dict(
            os.environ,
            {"GEMINI_IMAGE_MODEL": "gemini-3-pro-image"},
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "模型"):
                gen_image.validate_locked_model("gemini", plan)


class NativeImportTests(unittest.TestCase):
    def test_import_converts_jpeg_payload_to_png_and_crops(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.jpg"
            target = Path(tmp) / "page.png"
            Image.new("RGB", (1200, 900), "red").save(source, format="JPEG")

            gen_image.import_native_artifact(source, target)

            with Image.open(target) as image:
                self.assertEqual(image.format, "PNG")
                self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)

    def test_import_accepts_source_already_at_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "page.png"
            Image.new("RGB", (1600, 900), "blue").save(target, format="PNG")

            gen_image.import_native_artifact(target, target)

            with Image.open(target) as image:
                self.assertEqual(image.size, (1600, 900))

    def test_cli_native_import_updates_page_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ppt_workspace"
            pages = workspace / "pages"
            pages.mkdir(parents=True)
            source = Path(tmp) / "agy-output.jpg"
            Image.new("RGB", (1200, 900), "green").save(source, format="JPEG")
            plan = {
                "provider": "agy",
                "image_transport": "native",
                "image_model": "gemini-3.1-flash-image",
                "style": None,
                "pages": [{
                    "id": "P01",
                    "status": "prompted",
                    "prompt_file": "prompts/P01.txt",
                    "image": "pages/P01.png",
                }],
            }
            (workspace / "plan.json").write_text(
                json.dumps(plan), encoding="utf-8"
            )
            env = os.environ.copy()
            env["PPTC_WORKSPACE"] = str(workspace)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "gen_image.py"),
                    "--page",
                    "P01",
                    "--provider",
                    "agy",
                    "--transport",
                    "native",
                    "--import-file",
                    str(source),
                ],
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            updated = json.loads(
                (workspace / "plan.json").read_text(encoding="utf-8")
            )
            self.assertEqual(updated["pages"][0]["status"], "generated")
            self.assertIsNotNone(
                updated["pages"][0]["image_input_hash"]
            )
            with Image.open(pages / "P01.png") as image:
                self.assertEqual(image.format, "PNG")
                self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)


if __name__ == "__main__":
    unittest.main()
