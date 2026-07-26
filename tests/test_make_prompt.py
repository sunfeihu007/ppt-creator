import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_prompt.py"


class LayeredPromptTests(unittest.TestCase):
    def run_prompt(self, plan):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ppt_workspace"
            workspace.mkdir()
            (workspace / "plan.json").write_text(
                json.dumps(plan, ensure_ascii=False), encoding="utf-8"
            )
            env = os.environ.copy()
            env["PPTC_WORKSPACE"] = str(workspace)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--page", "P01"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )
            prompt_path = workspace / "prompts" / "P01.txt"
            prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
            updated_plan = json.loads(
                (workspace / "plan.json").read_text(encoding="utf-8")
            )
            return result, prompt, updated_plan

    def test_composes_style_page_type_industry_and_semantic_palette(self):
        plan = {
            "topic": "测试",
            "audience": "客户",
            "palette": "finance-navy-teal",
            "style": "flat-editorial",
            "industry": "finance",
            "provider": "codex",
            "image_transport": "native",
            "image_model": "gpt-image-2",
            "pages": [{
                "id": "P01",
                "template": "arch",
                "page_type": "architecture",
                "title": "总体架构",
                "subtitle": "",
                "points": ["接入层", "平台层"],
                "layout_hint": "横向分层",
                "notes": "",
                "status": "pending",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
            }],
        }

        result, prompt, updated_plan = self.run_prompt(plan)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("flat editorial-consulting family", prompt)
        self.assertIn("PAGE TYPE — ARCHITECTURE", prompt)
        self.assertIn("INDUSTRY VISUAL — FINANCE", prompt)
        self.assertIn("- Title: 总体架构", prompt)
        self.assertLess(
            prompt.index("flat editorial-consulting family"),
            prompt.index("PAGE TYPE — ARCHITECTURE"),
        )
        self.assertLess(
            prompt.index("PAGE TYPE — ARCHITECTURE"),
            prompt.index("INDUSTRY VISUAL — FINANCE"),
        )
        self.assertLess(
            prompt.index("INDUSTRY VISUAL — FINANCE"),
            prompt.index("Page content (use EXACTLY this text, no additions)"),
        )
        self.assertEqual(updated_plan["pages"][0]["title"], "总体架构")
        self.assertEqual(updated_plan["pages"][0]["points"], ["接入层", "平台层"])
        self.assertNotIn("[COLOR_SCHEME]", prompt)
        self.assertNotIn("{STRUCTURE}", prompt)
        self.assertNotIn("{FOCUS}", prompt)

    def test_legacy_plan_resolves_template_and_general_industry(self):
        plan = {
            "topic": "测试",
            "audience": "客户",
            "palette": "orange-teal",
            "style": "swiss-grid",
            "provider": "codex",
            "image_transport": "native",
            "image_model": "gpt-image-2",
            "pages": [{
                "id": "P01",
                "template": "case",
                "title": "客户案例",
                "subtitle": "",
                "points": [],
                "layout_hint": "",
                "notes": "",
                "status": "pending",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
            }],
        }

        result, prompt, updated_plan = self.run_prompt(plan)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PAGE TYPE — CUSTOMER CASE", prompt)
        self.assertIn("INDUSTRY VISUAL — GENERAL BUSINESS", prompt)
        self.assertEqual(updated_plan["industry"], "general")
        self.assertEqual(updated_plan["pages"][0]["page_type"], "case")

    def test_prompt_includes_applicable_decision_and_provenance_label(self):
        plan = {
            "topic": "测试",
            "audience": "客户",
            "assurance_profile": "evidence-sensitive",
            "palette": "orange-teal",
            "style": "swiss-grid",
            "industry": "general",
            "provider": "codex",
            "image_transport": "native",
            "image_model": "gpt-image-2",
            "requirements": [{
                "id": "REQ-001",
                "decision": "平台名称统一为 Harness",
                "required_terms": ["Harness"],
                "affected_pages": ["P01"],
            }],
            "claim_constraints": [],
            "source_registry": [],
            "pages": [{
                "id": "P01",
                "template": "case",
                "page_type": "case",
                "title": "Harness 客户方案",
                "subtitle": "",
                "points": ["Harness 负责任务协同"],
                "layout_hint": "",
                "notes": "",
                "status": "pending",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
                "evidence_level": "conceptual",
                "provenance_label": "方案示意",
            }],
        }

        result, prompt, _updated_plan = self.run_prompt(plan)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PROJECT CONTRACT", prompt)
        self.assertIn("REQ-001: 平台名称统一为 Harness", prompt)
        self.assertIn("Visible provenance label (exact text): 方案示意", prompt)
        self.assertNotIn("source_registry", prompt)

    def test_forbidden_term_stops_prompt_generation(self):
        plan = {
            "topic": "测试",
            "audience": "客户",
            "palette": "orange-teal",
            "style": "swiss-grid",
            "industry": "general",
            "provider": "codex",
            "image_transport": "native",
            "image_model": "gpt-image-2",
            "requirements": [{
                "id": "REQ-001",
                "decision": "不得使用旧名称",
                "forbidden_terms": ["Hermes"],
                "affected_pages": ["P01"],
            }],
            "pages": [{
                "id": "P01",
                "template": "content",
                "page_type": "detail",
                "title": "Hermes 总体方案",
                "subtitle": "",
                "points": [],
                "layout_hint": "",
                "notes": "",
                "status": "pending",
                "prompt_file": "prompts/P01.txt",
                "image": "pages/P01.png",
            }],
        }

        result, prompt, _updated_plan = self.run_prompt(plan)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hermes", result.stderr)
        self.assertEqual(prompt, "")


if __name__ == "__main__":
    unittest.main()
