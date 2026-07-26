# PPT Creator v2.4 Project Contract & Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generic project fact contract, hash-based change propagation, semantic gates, exact page reuse, generated outline, and final synchronization to PPT Creator v2.4.

**Architecture:** Introduce `scripts/project_contract.py` as the single contract boundary shared by planning, prompting, generation, verification, and assembly. Keep current decisions and hashes in `plan.json`; keep generated outline, QA output, and delivery manifest as sidecar artifacts. Preserve the seven phases and normalize v2.3 plans without forcing regeneration.

**Tech Stack:** Python 3 standard library, Pillow, python-pptx, `unittest`, JSON and Markdown references.

---

### Task 1: Contract schema, validation, and compatibility

**Files:**
- Create: `scripts/project_contract.py`
- Create: `tests/test_project_contract.py`
- Modify: `scripts/plan_tool.py`
- Test: `tests/test_project_contract.py`
- Test: `tests/test_plan_tool.py`

- [x] **Step 1: Write failing tests for v2.4 normalization and validation**

Add tests that call the desired API:

```python
plan = project_contract.normalize_plan(legacy_plan)
self.assertEqual(plan["schema_version"], "2.4")
self.assertEqual(plan["assurance_profile"], "standard")
self.assertEqual(plan["delivery_mode"], "raster_slide")
self.assertEqual(plan["requirements"], [])
self.assertEqual(plan["pages"][0]["source_refs"], [])

with self.assertRaisesRegex(project_contract.ContractError, "重复"):
    project_contract.normalize_plan(plan_with_duplicate_requirement_ids)
```

Also assert invalid profiles, unsupported delivery modes, missing rule/source references, missing
reuse sources, self-reuse, and reuse cycles raise `ContractError`.

- [x] **Step 2: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_project_contract -v
```

Expected: import failure because `scripts/project_contract.py` does not exist.

- [x] **Step 3: Implement the minimal contract module**

Implement:

```python
class ContractError(ValueError):
    pass

ASSURANCE_PROFILES = {"standard", "client-facing", "evidence-sensitive"}
DELIVERY_MODES = {"raster_slide"}

def normalize_plan(plan):
    plan.setdefault("schema_version", "2.4")
    plan.setdefault("assurance_profile", "standard")
    plan.setdefault("delivery_mode", "raster_slide")
    plan.setdefault("requirements", [])
    plan.setdefault("claim_constraints", [])
    plan.setdefault("source_registry", [])
    for page in plan.get("pages", []):
        page.setdefault("requirement_refs", [])
        page.setdefault("claim_refs", [])
        page.setdefault("source_refs", [])
        page.setdefault("asset_provenance", [])
        page.setdefault("evidence_level", None)
        page.setdefault("provenance_label", "")
        page.setdefault("reused_from", None)
        page.setdefault("reuse_mode", None)
        page.setdefault("dirty_reasons", [])
        page.setdefault("prompt_input_hash", None)
        page.setdefault("image_input_hash", None)
    validate_plan(plan)
    adopt_legacy_hashes(plan)
    return plan
```

Implement ID registries, reference validation, supported profile/mode checks, and depth-first reuse
cycle detection. Import and call `normalize_plan` from `plan_tool.load()` and `cmd_init()`, converting
`ContractError` to the existing `[plan_tool]` exit format.

- [x] **Step 4: Run focused and existing plan tests**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_plan_tool -v
```

Expected: all tests pass.

- [x] **Step 5: Commit schema support**

```bash
git add scripts/project_contract.py scripts/plan_tool.py tests/test_project_contract.py tests/test_plan_tool.py
git commit -m "feat: add v2.4 project contract schema"
```

### Task 2: Semantic lint and assurance profiles

**Files:**
- Modify: `scripts/project_contract.py`
- Modify: `scripts/plan_tool.py`
- Modify: `scripts/make_prompt.py`
- Modify: `tests/test_project_contract.py`
- Modify: `tests/test_make_prompt.py`

- [x] **Step 1: Write failing lint tests**

Cover exact affected-page behavior:

```python
findings = project_contract.lint_pages(plan)
self.assertIn(("error", "P01", "REQ-001"), finding_keys(findings))
self.assertNotIn(("error", "P02", "REQ-001"), finding_keys(findings))
```

Test forbidden terms, required terms, invalid source refs, `client-facing` case warnings,
`evidence-sensitive` verified cases without sources, and conceptual cases without a provenance
label. Add a prompt test proving an applicable decision block and visible provenance label are
included, and a forbidden term prevents prompt creation.

- [x] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_make_prompt -v
```

Expected: failures because `lint_pages()` and prompt contract composition are missing.

- [x] **Step 3: Implement lint and prompt contract composition**

Implement:

```python
def applicable_entries(plan, page, collection, refs_field):
    refs = set(page.get(refs_field, []))
    return [
        item for item in plan.get(collection, [])
        if item["id"] in refs
        or not item.get("affected_pages")
        or "all" in item["affected_pages"]
        or page["id"] in item["affected_pages"]
    ]

def lint_pages(plan, page_ids=None, text_overrides=None, strict=False):
    # Return [{"severity": "error|warning", "page": "P01",
    #          "rule_id": "REQ-001", "message": "..."}]
```

Add `plan_tool.py lint --ids all`. Before writing a prompt, `make_prompt.py` must normalize the plan,
run lint for the selected page, stop on errors, and append project decisions plus provenance
instructions without exposing source file paths.

- [x] **Step 4: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_make_prompt -v
```

Expected: all tests pass.

- [x] **Step 5: Commit semantic lint**

```bash
git add scripts/project_contract.py scripts/plan_tool.py scripts/make_prompt.py tests/test_project_contract.py tests/test_make_prompt.py
git commit -m "feat: enforce project claims and evidence rules"
```

### Task 3: Hash-based invalidation and deterministic update commands

**Files:**
- Modify: `scripts/project_contract.py`
- Modify: `scripts/plan_tool.py`
- Modify: `scripts/make_prompt.py`
- Modify: `scripts/gen_image.py`
- Modify: `tests/test_project_contract.py`
- Modify: `tests/test_plan_tool.py`
- Modify: `tests/test_make_prompt.py`
- Modify: `tests/test_gen_image.py`

- [ ] **Step 1: Write failing hash and invalidation tests**

Test that:

```python
old = project_contract.expected_page_hash(plan, page)
plan["requirements"][0]["forbidden_terms"].append("NewTerm")
changed = project_contract.invalidate_stale_pages(plan)
self.assertEqual(changed, ["P01"])
self.assertEqual(page["status"], "pending")
self.assertIn("project_input_changed", page["dirty_reasons"])
```

Also test unrelated pages remain approved, global style/provider changes invalidate all pages,
`make_prompt.py` records `prompt_input_hash`, `gen_image.py` records `image_input_hash`, and
`plan_tool.py pages --status generated` records hashes for `--no-state` worker output.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_plan_tool tests.test_make_prompt tests.test_gen_image -v
```

Expected: failures because hash APIs and recording are missing.

- [ ] **Step 3: Implement canonical hashing and stale propagation**

Implement stable JSON hashing:

```python
def stable_hash(value):
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def expected_page_hash(plan, page_id, _stack=None):
    # Hash page-visible content, applicable rules/sources, design lock,
    # provenance, and recursively resolved exact-reuse source input.
```

Implement `invalidate_stale_pages(plan)`, `record_prompt_hash(plan, page)`,
`record_image_hash(plan, page)`, and `sync_findings(plan)`. Add:

```bash
plan_tool.py contract --file project_contract.json
plan_tool.py page --id P01 --patch page_patch.json
plan_tool.py sync
plan_tool.py sync-check
```

`cmd_design` and `cmd_provider` must invalidate all affected generated pages when the lock changes.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_plan_tool tests.test_make_prompt tests.test_gen_image -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit change propagation**

```bash
git add scripts/project_contract.py scripts/plan_tool.py scripts/make_prompt.py scripts/gen_image.py tests
git commit -m "feat: invalidate stale PPT artifacts by content hash"
```

### Task 4: Exact page reuse, optional OCR verification, and final synchronization

**Files:**
- Create: `scripts/verify_semantics.py`
- Create: `tests/test_verify_semantics.py`
- Modify: `scripts/project_contract.py`
- Modify: `scripts/plan_tool.py`
- Modify: `scripts/make_prompt.py`
- Modify: `scripts/verify_pages.py`
- Modify: `scripts/build_ppt.py`
- Create: `tests/test_build_ppt.py`
- Modify: `tests/test_project_contract.py`

- [ ] **Step 1: Write failing reuse, OCR, outline, and build-gate tests**

Test:

```python
self.assertEqual(
    project_contract.effective_image(plan, "P04"),
    "pages/P02.png",
)
self.assertEqual(
    project_contract.render_outline(plan),
    expected_markdown,
)
```

Add subprocess tests proving reused pages do not generate prompts, OCR forbidden terms fail,
missing OCR is optional, `--strict` promotes title/required-term warnings to errors, stale approved
pages block build, and a valid build writes both `final_outline.md` and
`artifact_manifest.json`.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_verify_semantics tests.test_build_ppt -v
```

Expected: failures because reuse resolution, OCR adapter, outline export, and sync build gate are
missing.

- [ ] **Step 3: Implement exact reuse and optional OCR adapter**

Add `effective_page()` / `effective_image()` helpers. `make_prompt.py` exits successfully with an
exact-reuse notice and no prompt. `verify_pages.py` and `build_ppt.py` resolve source images while
retaining alias-page notes.

Implement:

```bash
python scripts/verify_semantics.py --ocr-dir ppt_workspace/qa/ocr
python scripts/verify_semantics.py --ocr-dir ppt_workspace/qa/ocr --strict --require-ocr
python scripts/plan_tool.py reuse --id P04 --from P02
python scripts/plan_tool.py export-outline --out ppt_workspace/final_outline.md
```

- [ ] **Step 4: Implement final sync and manifest**

Before assembly, `build_ppt.py` must normalize, lint, and reject stale input hashes. It then exports
the final outline and writes:

```json
{
  "schema_version": "2.4",
  "delivery_mode": "raster_slide",
  "pptx": {"file": "...", "bytes": 1234, "pages": 2},
  "notes_count": 2,
  "source_images": [
    {"page": "P01", "resolved_from": "P01", "file": "pages/P01.png",
     "width": 1600, "height": 900, "sha256": "..."}
  ]
}
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 -m unittest tests.test_project_contract tests.test_verify_semantics tests.test_build_ppt -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit reuse and synchronization**

```bash
git add scripts/project_contract.py scripts/plan_tool.py scripts/make_prompt.py scripts/verify_semantics.py scripts/verify_pages.py scripts/build_ppt.py tests
git commit -m "feat: add exact reuse and final sync gate"
```

### Task 5: Skill workflow, docs, evals, and release metadata

**Files:**
- Modify: `SKILL.md`
- Create: `references/project-contract.md`
- Modify: `references/phases/phase1-3-planning.md`
- Modify: `references/phases/phase5-6-generation.md`
- Modify: `references/phases/phase7-assembly.md`
- Modify: `references/constraints.md`
- Modify: `README.md`
- Modify: `evals/evals.json`
- Modify: `tests/test_design_system.py`

- [ ] **Step 1: Write a failing release-structure test**

Assert:

```python
self.assertIn("v2.4.0", skill_text)
self.assertIn("references/project-contract.md", skill_text)
self.assertIn("plan_tool.py sync-check", skill_text)
self.assertIn("verify_semantics.py", skill_text)
```

Also assert eval IDs are unique and new evals cover general, finance, manufacturing, and port
contract behavior.

- [ ] **Step 2: Run the release test and verify RED**

Run:

```bash
python3 -m unittest tests.test_design_system -v
```

Expected: failure because v2.4 documentation is absent.

- [ ] **Step 3: Update the Skill with progressive disclosure**

Keep `SKILL.md` concise. Add only:

- v2.4 version and fact-contract first principle;
- the assurance-profile selection rule;
- script quick-reference commands;
- mandatory prompt lint / final sync behavior;
- a direct link to `references/project-contract.md`.

Put complete schema, examples, assurance rules, change propagation, OCR adapter, and migration
details in `references/project-contract.md`. Integrate checks into existing phases rather than
adding numbered phases.

- [ ] **Step 4: Update README and evals**

Document v2.4 behavior, current raster-only delivery mode, compatibility, commands, output files,
and the distinction between generated outline, semantic report, manifest, and `plan.json`.
Add evals for:

- a general internal deck with no sources;
- a finance case requiring evidence;
- a manufacturing terminology correction;
- a port conceptual case requiring “方案示意”;
- exact navigation-page reuse;
- a stale approved page blocking build.

- [ ] **Step 5: Run release tests and validation**

Run:

```bash
python3 -m unittest tests.test_design_system -v
python3 scripts/validate_design.py
python3 /Users/sunshuo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit release documentation**

```bash
git add SKILL.md README.md references evals tests/test_design_system.py
git commit -m "docs: release PPT Creator v2.4 project contract"
```

### Task 6: Full regression, requirement audit, merge, push, and local installation

**Files:**
- Verify: all tracked files
- Update externally after merge: `~/.agents/skills/ppt-creator`
- Update externally after merge: `~/.codex/skills/ppt-creator`

- [ ] **Step 1: Run the full regression suite**

Run:

```bash
python3 -m unittest discover -v
python3 scripts/validate_design.py
python3 /Users/sunshuo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
git diff --check
```

Expected: all tests pass, both validators pass, and `git diff --check` prints nothing.

- [ ] **Step 2: Audit the approved scope**

Verify each design requirement against code/tests and confirm no implementation of editable-native
rendering, mandatory OCR, cost accounting, new visual resources, or extra numbered phases entered
the release.

- [ ] **Step 3: Merge the feature branch into local main**

From the primary repository:

```bash
git checkout main
git merge --ff-only feat/project-contract-sync
python3 -m unittest discover -v
```

Expected: fast-forward merge and all tests pass on `main`.

- [ ] **Step 4: Push GitHub main**

```bash
git push origin main
```

Expected: GitHub reports `main` advanced to the v2.4 release commit.

- [ ] **Step 5: Synchronize both local Skill installations**

Use the repository installation workflow or replace the two installed copies from the verified
GitHub/main source. Then run:

```bash
rg -n "v2.4.0" ~/.agents/skills/ppt-creator/SKILL.md
rg -n "v2.4.0" ~/.codex/skills/ppt-creator/SKILL.md
python3 ~/.agents/skills/ppt-creator/scripts/plan_tool.py --help
python3 ~/.codex/skills/ppt-creator/scripts/plan_tool.py --help
```

Expected: both installations report v2.4.0 and both CLIs expose `lint`, `sync`, `sync-check`,
`reuse`, and `export-outline`.
