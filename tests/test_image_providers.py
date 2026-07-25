import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import image_providers  # noqa: E402


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class ProviderDetectionTests(unittest.TestCase):
    def test_other_client_auto_uses_gemini_key_not_installed_codex(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "secret"}, clear=True):
            with mock.patch("image_providers.shutil.which", return_value="/usr/bin/codex"):
                self.assertEqual(image_providers.detect_script_provider(), "gemini")

    def test_other_client_without_key_has_actionable_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                image_providers.detect_script_provider()

    def test_stable_gemini_model_is_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                image_providers.gemini_model(),
                "gemini-3.1-flash-image",
            )

    def test_provider_availability_uses_credentials_or_binary(self):
        with mock.patch.dict(os.environ, {"GOOGLE_API_KEY": "secret"}, clear=True):
            with mock.patch(
                "image_providers.shutil.which",
                side_effect=lambda name: f"/usr/bin/{name}" if name == "agy" else None,
            ):
                self.assertTrue(image_providers.provider_available("gemini"))
                self.assertTrue(image_providers.provider_available("agy"))
                self.assertFalse(image_providers.provider_available("codex"))

    def test_unknown_provider_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            image_providers.generate("unknown", "prompt", "out.png", [])


class GeminiAdapterTests(unittest.TestCase):
    def test_gemini_uses_stable_model_and_header_key(self):
        image_bytes = b"image payload"
        payload = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": base64.b64encode(image_bytes).decode(),
                        }
                    }]
                }
            }]
        }
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "page.png"
            with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "top-secret"}, clear=True):
                with mock.patch(
                    "image_providers.urllib.request.urlopen",
                    return_value=FakeResponse(payload),
                ) as urlopen:
                    image_providers.generate_gemini("prompt", out_path, [])

            request = urlopen.call_args.args[0]
            self.assertIn("gemini-3.1-flash-image:generateContent", request.full_url)
            self.assertNotIn("top-secret", request.full_url)
            self.assertEqual(request.get_header("X-goog-api-key"), "top-secret")
            self.assertEqual(out_path.read_bytes(), image_bytes)


class CliAdapterTests(unittest.TestCase):
    def test_codex_command_requests_exact_output_without_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "page.png"

            def fake_run(command, **_kwargs):
                out_path.write_bytes(b"generated")
                return subprocess.CompletedProcess(command, 0, "", "")

            with mock.patch.dict(
                os.environ,
                {"GEMINI_API_KEY": "must-not-leak", "PPTC_CODEX_BIN": "codex-test"},
                clear=True,
            ):
                with mock.patch("image_providers.subprocess.run", side_effect=fake_run) as run:
                    image_providers.generate_codex("hello", out_path, [])

            command_text = " ".join(run.call_args.args[0])
            self.assertIn(str(out_path.resolve()), command_text)
            self.assertNotIn("must-not-leak", command_text)

    def test_agy_preflight_rejects_empty_print_response(self):
        completed = subprocess.CompletedProcess(["agy"], 0, "", "")
        with mock.patch("image_providers.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "preflight"):
                image_providers.preflight_agy()

    def test_agy_artifact_discovery_uses_name_and_start_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / "P01-token_old.jpg"
            wrong = root / "P02-token_new.jpg"
            match = root / "nested" / "P01-token_new.png"
            match.parent.mkdir()
            old.write_bytes(b"old")
            wrong.write_bytes(b"wrong")
            started_at = time.time()
            match.write_bytes(b"new")
            os.utime(old, (started_at - 5, started_at - 5))
            os.utime(wrong, (started_at + 1, started_at + 1))
            os.utime(match, (started_at + 1, started_at + 1))

            found = image_providers.find_agy_artifact(
                root, "P01-token", started_at
            )

            self.assertEqual(found, match)


if __name__ == "__main__":
    unittest.main()
