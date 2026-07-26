import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_semantics.py"


def semantic_plan():
    return {
        "topic": "测试",
        "audience": "客户",
        "requirements": [{
            "id": "REQ-001",
            "decision": "平台名称统一为 Harness",
            "required_terms": ["Harness"],
            "forbidden_terms": ["Hermes"],
            "affected_pages": ["P01"],
        }],
        "pages": [{
            "id": "P01",
            "template": "content",
            "page_type": "detail",
            "title": "Harness 总体方案",
            "points": ["Harness 负责任务协同"],
            "status": "generated",
            "prompt_file": "prompts/P01.txt",
            "image": "pages/P01.png",
        }],
    }


class SemanticVerificationTests(unittest.TestCase):
    def run_verify(self, plan, ocr_text=None, *extra_args):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ppt_workspace"
            ocr_dir = workspace / "qa" / "ocr"
            ocr_dir.mkdir(parents=True)
            (workspace / "plan.json").write_text(
                json.dumps(plan, ensure_ascii=False), encoding="utf-8"
            )
            if ocr_text is not None:
                (ocr_dir / "P01.txt").write_text(
                    ocr_text, encoding="utf-8"
                )
            env = os.environ.copy()
            env["PPTC_WORKSPACE"] = str(workspace)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--ocr-dir",
                    str(ocr_dir),
                    *extra_args,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )
            report_path = workspace / "qa" / "semantic-report.json"
            report = (
                json.loads(report_path.read_text(encoding="utf-8"))
                if report_path.exists()
                else None
            )
            return result, report

    def test_forbidden_ocr_term_fails(self):
        result, report = self.run_verify(
            semantic_plan(), "Harness 总体方案\nHermes 负责协同"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hermes", result.stdout + result.stderr)
        self.assertEqual(report["status"], "failed")

    def test_missing_ocr_is_optional_by_default(self):
        result, report = self.run_verify(semantic_plan())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SKIPPED", result.stdout)
        self.assertEqual(report["status"], "passed")

    def test_require_ocr_fails_when_text_is_missing(self):
        result, report = self.run_verify(
            semantic_plan(), None, "--require-ocr"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OCR-MISSING", result.stdout + result.stderr)
        self.assertEqual(report["status"], "failed")

    def test_missing_title_and_required_term_warn_or_fail_in_strict_mode(self):
        result, report = self.run_verify(semantic_plan(), "其他文字")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["status"], "passed")
        self.assertTrue(
            any(item["severity"] == "warning" for item in report["findings"])
        )

        strict_result, strict_report = self.run_verify(
            semantic_plan(), "其他文字", "--strict"
        )
        self.assertNotEqual(strict_result.returncode, 0)
        self.assertEqual(strict_report["status"], "failed")


if __name__ == "__main__":
    unittest.main()
