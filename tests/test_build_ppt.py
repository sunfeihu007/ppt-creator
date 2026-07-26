import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import project_contract  # noqa: E402


def build_plan():
    plan = {
        "topic": "同步测试",
        "audience": "客户",
        "assurance_profile": "standard",
        "delivery_mode": "raster_slide",
        "palette": "orange-teal",
        "style": "swiss-grid",
        "industry": "general",
        "provider": "codex",
        "image_transport": "native",
        "image_model": "gpt-image-2",
        "requirements": [],
        "claim_constraints": [],
        "source_registry": [],
        "pages": [
            {
                "id": "P01",
                "template": "content",
                "page_type": "detail",
                "title": "统一导览",
                "points": ["统一协同"],
                "notes": "【普通页】3-4分钟",
                "status": "approved",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
            },
            {
                "id": "P02",
                "template": "content",
                "page_type": "detail",
                "title": "统一导览",
                "points": ["统一协同"],
                "notes": "【过渡页】1-2分钟",
                "status": "approved",
                "prompt_file": "prompts/P02.txt",
                "image": "pages/P02.png",
                "reused_from": "P01",
                "reuse_mode": "exact_asset",
            },
        ],
    }
    plan = project_contract.normalize_plan(plan)
    for page in plan["pages"]:
        project_contract.record_prompt_hash(plan, page)
        project_contract.record_image_hash(plan, page)
    return plan


class BuildSynchronizationTests(unittest.TestCase):
    def run_build(self, mutate=None):
        temp = tempfile.TemporaryDirectory()
        workspace = Path(temp.name) / "ppt_workspace"
        pages = workspace / "pages"
        output = workspace / "output"
        pages.mkdir(parents=True)
        output.mkdir()
        Image.new("RGB", (1600, 900), "white").save(
            pages / "P01.png", format="PNG"
        )
        plan = build_plan()
        if mutate:
            mutate(plan)
        (workspace / "plan.json").write_text(
            json.dumps(plan, ensure_ascii=False), encoding="utf-8"
        )
        env = os.environ.copy()
        env["PPTC_WORKSPACE"] = str(workspace)
        out = output / "test.pptx"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "build_ppt.py"),
                "--out",
                str(out),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )
        return temp, workspace, out, result

    def test_stale_approved_page_blocks_build(self):
        temp, _workspace, _out, result = self.run_build(
            lambda plan: plan["pages"][0].update({"title": "已修改标题"})
        )
        self.addCleanup(temp.cleanup)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("STALE", result.stderr)

    def test_blocked_visual_combination_blocks_build_before_stale_check(self):
        temp, _workspace, _out, result = self.run_build(
            lambda plan: plan.update(
                {"palette": "swiss-ikb", "style": "glass-3d"}
            )
        )
        self.addCleanup(temp.cleanup)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DESIGN GATE FAILED", result.stderr)
        self.assertIn("blocked-combination", result.stderr)

    def test_valid_build_reuses_source_and_writes_outline_and_manifest(self):
        temp, workspace, out, result = self.run_build()
        self.addCleanup(temp.cleanup)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(out.exists())
        self.assertTrue((workspace / "final_outline.md").exists())
        manifest_path = workspace / "output" / "artifact_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "2.4")
        self.assertEqual(manifest["delivery_mode"], "raster_slide")
        self.assertEqual(manifest["pptx"]["pages"], 2)
        self.assertEqual(manifest["notes_count"], 2)
        self.assertEqual(
            manifest["source_images"][1]["resolved_from"], "P01"
        )
        self.assertEqual(
            manifest["source_images"][0]["sha256"],
            manifest["source_images"][1]["sha256"],
        )

    def test_verify_pages_accepts_reused_page_without_duplicate_file(self):
        temp, workspace, _out, _result = self.run_build()
        self.addCleanup(temp.cleanup)
        env = os.environ.copy()
        env["PPTC_WORKSPACE"] = str(workspace)

        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "verify_pages.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("P02", result.stdout)


if __name__ == "__main__":
    unittest.main()
