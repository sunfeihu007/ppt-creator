# AGY Native Image Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release PPT Creator v2.2.0 with AGY-native Gemini image generation in AGY, Codex-native ImageGen in Codex, and stable Gemini API generation in other clients, while locking one provider/model per presentation.

**Architecture:** Host-native image tools are selected by `SKILL.md` instructions and their artifacts are imported through the shared image finalizer. Scripted API/CLI backends live in a focused provider module; `plan.json` stores logical provider, transport, and model so generation cannot silently switch mid-deck. Standard-library unit tests mock credentials, binaries, subprocesses, and HTTP calls.

**Tech Stack:** Python 3 standard library, Pillow, python-pptx, unittest, AGY CLI, Codex CLI, Gemini REST API.

---

## File Structure

- Create `scripts/image_providers.py`: provider constants, credential/binary detection, Gemini API adapter, Codex CLI adapter, experimental AGY CLI adapter and preflight.
- Modify `scripts/gen_image.py`: provider resolution, lock enforcement, native-artifact import, retry/finalization orchestration.
- Modify `scripts/plan_tool.py`: persist and validate `provider`, `image_transport`, and `image_model`.
- Create `tests/test_image_providers.py`: provider detection, model, HTTP, CLI, and credential-safety tests.
- Create `tests/test_plan_tool.py`: plan metadata and backward-compatibility tests.
- Create `tests/test_gen_image.py`: routing/locking/native-import tests.
- Modify `SKILL.md`: v2.2.0 host-native routing instructions.
- Modify `references/phases/phase4-design.md`: capability selection and preflight lock procedure.
- Modify `references/phases/phase5-6-generation.md`: AGY/Codex native worker instructions and import procedure.
- Modify `README.md`: v2.2.0 routing table, models, installation paths, migration notes.
- Modify `evals/evals.json`: AGY, Codex, other-client, and no-mixing behavior cases.

### Task 1: Provider Adapter Module

**Files:**
- Create: `scripts/image_providers.py`
- Create: `tests/test_image_providers.py`

- [ ] **Step 1: Write failing provider-selection tests**

```python
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
```

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_image_providers -v`  
Expected: FAIL because `scripts/image_providers.py` does not exist.

- [ ] **Step 3: Implement provider constants and availability**

```python
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-image"
DEFAULT_CODEX_MODEL = "gpt-image-2"
AGY_BIN = os.environ.get("PPTC_AGY_BIN", "agy")
CODEX_BIN = os.environ.get("PPTC_CODEX_BIN", "codex")

def gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def gemini_model():
    return os.environ.get("GEMINI_IMAGE_MODEL", DEFAULT_GEMINI_MODEL)

def detect_script_provider():
    if gemini_key():
        return "gemini"
    raise RuntimeError(
        "其他客户端默认通过 Gemini API 生图；请设置 GEMINI_API_KEY 或 "
        "GOOGLE_API_KEY。不要把 key 粘贴到对话中。"
    )

def provider_available(name):
    if name == "gemini":
        return bool(gemini_key())
    binary = AGY_BIN if name == "agy" else CODEX_BIN
    return bool(shutil.which(binary))
```

- [ ] **Step 4: Add failing adapter tests**

Test that Gemini sends the key only in `x-goog-api-key`, uses the stable model URL, and writes decoded image bytes. Test that Codex and AGY command construction contains the output path but not environment credentials. Test that AGY preflight rejects an empty `agy -p` response and that AGY artifact discovery accepts only matching files newer than the request start time.

- [ ] **Step 5: Implement the three scripted adapters**

Expose exactly five public call points: `generate_gemini(prompt, out_path, refs, timeout=300)`,
`generate_codex(prompt, out_path, refs, timeout=600)`, `preflight_agy(timeout=60)`,
`generate_agy(prompt, out_path, refs, timeout=600)`, and
`generate(provider, prompt, out_path, refs, timeout=None)`. The dispatcher accepts only
`agy`, `codex`, or `gemini`, assigns the provider-specific default timeout when `timeout` is
`None`, and raises `ValueError` for every other value.

`preflight_agy()` runs an `agy -p` text probe and requires the expected marker in stdout. `generate_agy()` calls preflight, uses a unique `ImageName`, records the start timestamp, asks AGY to call `generate_image` with 16:9 output, finds a matching JPG/PNG beneath `PPTC_AGY_BRAIN_DIR` or `~/.gemini/antigravity-cli/brain`, and copies it to `out_path`. It warns that native AGY currently has no dedicated reference-image argument and embeds reference guidance in the prompt instead.

- [ ] **Step 6: Run provider tests**

Run: `python -m unittest tests.test_image_providers -v`  
Expected: all provider tests PASS without making network calls or consuming image credits.

- [ ] **Step 7: Commit**

```bash
git add scripts/image_providers.py tests/test_image_providers.py
git commit -m "feat: add AGY Codex and Gemini image adapters"
```

### Task 2: Plan Metadata and Provider Lock

**Files:**
- Modify: `scripts/plan_tool.py`
- Create: `tests/test_plan_tool.py`

- [ ] **Step 1: Write failing plan metadata tests**

Create temporary workspaces and assert:

```python
def test_design_locks_provider_transport_and_model(self):
    run_plan_tool(
        "design", "--palette", "orange-teal", "--style", "glass-3d",
        "--provider", "agy", "--transport", "native"
    )
    plan = load_plan()
    self.assertEqual(plan["provider"], "agy")
    self.assertEqual(plan["image_transport"], "native")
    self.assertEqual(plan["image_model"], "gemini-3.1-flash-image")

def test_old_plan_without_metadata_still_loads(self):
    write_plan({"provider": "gemini", "pages": [], "review": {}})
    plan = plan_tool.load()
    self.assertEqual(plan["image_transport"], "api")
    self.assertEqual(plan["image_model"], "gemini-3.1-flash-image")
```

Also test invalid combinations: `gemini/native`, `codex/api`, and `agy/api`.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_plan_tool -v`  
Expected: FAIL because transport/model fields and options do not exist.

- [ ] **Step 3: Implement metadata normalization**

Add:

```python
PROVIDER_TRANSPORTS = {
    "agy": {"native", "cli"},
    "codex": {"native", "cli"},
    "gemini": {"api"},
}
DEFAULT_MODELS = {
    "agy": "gemini-3.1-flash-image",
    "codex": "gpt-image-2",
    "gemini": "gemini-3.1-flash-image",
}

def default_transport(provider):
    return {"agy": "native", "codex": "native", "gemini": "api"}[provider]

def normalize_image_config(plan):
    provider = plan.get("provider")
    if provider == "codex-builtin":
        provider = "codex"
        plan["provider"] = provider
        plan.setdefault("image_transport", "native")
    if provider in PROVIDER_TRANSPORTS:
        plan.setdefault("image_transport", default_transport(provider))
        plan.setdefault("image_model", DEFAULT_MODELS[provider])
    return plan
```

Use it from `load()`. Initialize new fields to `None`. Add `--transport` and `--model` to `design` and `provider`; validate legal combinations before saving. Status output prints `provider/transport/model`.

- [ ] **Step 4: Run plan tests**

Run: `python -m unittest tests.test_plan_tool -v`  
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/plan_tool.py tests/test_plan_tool.py
git commit -m "feat: lock image provider transport and model"
```

### Task 3: Generation Routing and Native Artifact Import

**Files:**
- Modify: `scripts/gen_image.py`
- Create: `tests/test_gen_image.py`

- [ ] **Step 1: Write failing routing tests**

Test the pure routing function:

```python
def test_auto_uses_locked_script_transport(self):
    plan = {"provider": "gemini", "image_transport": "api"}
    self.assertEqual(resolve_provider("auto", None, plan), ("gemini", "api"))

def test_auto_rejects_native_lock_in_script(self):
    plan = {"provider": "agy", "image_transport": "native"}
    with self.assertRaisesRegex(RuntimeError, "generate_image"):
        resolve_provider("auto", None, plan)

def test_explicit_provider_cannot_override_lock(self):
    plan = {"provider": "codex", "image_transport": "native"}
    with self.assertRaisesRegex(RuntimeError, "plan_tool.py provider"):
        resolve_provider("gemini", "api", plan)

def test_both_is_rejected_after_provider_lock(self):
    with self.assertRaisesRegex(RuntimeError, "锁定"):
        resolve_provider("both", None, {"provider": "gemini"})
```

- [ ] **Step 2: Write failing native-import tests**

Create a temporary JPEG source and a plan targeting `pages/P01.png`. Run the import helper and assert that:

- the target exists and opens as PNG;
- it is cropped to 16:9;
- page state becomes `generated` unless `--no-state` is used;
- importing a source already at the target path does not raise `SameFileError`;
- a native import must match the locked provider/transport.

- [ ] **Step 3: Run tests and verify failure**

Run: `python -m unittest tests.test_gen_image -v`  
Expected: FAIL because the routing and import helpers do not exist.

- [ ] **Step 4: Refactor generation orchestration**

Import `image_providers` and expose:

```python
def resolve_provider(requested_provider, requested_transport, plan):
    locked_provider = canonical_provider(plan.get("provider"))
    locked_transport = plan.get("image_transport")
    if requested_provider == "auto":
        if locked_provider:
            if locked_transport == "native":
                tool = "generate_image" if locked_provider == "agy" else "image_gen"
                raise RuntimeError(
                    f"plan.json 已锁定 {locked_provider}/native；请由当前 agent 调用原生 "
                    f"{tool}，再用 --import-file 导入。"
                )
            return locked_provider, locked_transport
        return image_providers.detect_script_provider(), "api"
    if requested_provider == "both":
        if locked_provider:
            raise RuntimeError("设计已锁定，禁止用 both 混合后端")
        return "both", None
    transport = requested_transport or (
        "api" if requested_provider == "gemini" else "cli"
    )
    if locked_provider and (
        requested_provider != locked_provider or
        (locked_transport and transport != locked_transport)
    ):
        raise RuntimeError(
            "显式后端与 plan.json 锁定不一致；先用 plan_tool.py provider 正式切换。"
        )
    return requested_provider, transport
```

Replace in-file Gemini/Codex functions with `image_providers.generate()`. Keep retry, image validation, history, and final state update in `gen_image.py`.

- [ ] **Step 5: Add native artifact import**

Add CLI options:

```python
ap.add_argument("--transport", choices=["native", "cli", "api"])
ap.add_argument("--import-file",
                help="导入当前 agent 原生生图工具产物并执行裁切/状态更新")
```

When `--import-file` is present, require `--provider agy|codex --transport native`, verify it matches the lock, copy/convert the source to the page output, run `postprocess()`, and call `finalize()`. Save PNG explicitly so a JPEG payload never remains under a misleading `.png` extension.

- [ ] **Step 6: Tighten comparison behavior**

Permit `both` only before a provider lock and only for the explicit CLI/API pair `codex` and `gemini`. Require the user to select a winner and then lock it with `plan_tool.py provider`; do not automatically mix a comparison artifact into an already locked deck.

- [ ] **Step 7: Run generation tests**

Run: `python -m unittest tests.test_gen_image -v`  
Expected: all tests PASS.

- [ ] **Step 8: Run the whole unit suite**

Run: `python -m unittest discover -s tests -v`  
Expected: all tests PASS with no external calls.

- [ ] **Step 9: Commit**

```bash
git add scripts/gen_image.py tests/test_gen_image.py
git commit -m "feat: enforce image routing and native imports"
```

### Task 4: Skill Workflow, README, and Evaluations

**Files:**
- Modify: `SKILL.md`
- Modify: `references/phases/phase4-design.md`
- Modify: `references/phases/phase5-6-generation.md`
- Modify: `README.md`
- Modify: `evals/evals.json`

- [ ] **Step 1: Update the skill version and default routing**

Set the displayed version to v2.2.0. Replace “Codex first” with:

1. AGY native `generate_image` → `agy/native/gemini-3.1-flash-image`.
2. Codex native `image_gen` → `codex/native/gpt-image-2`.
3. Other clients with API key → `gemini/api/gemini-3.1-flash-image`.
4. Explicit `agy/cli` and `codex/cli` compatibility bridges only.

State that provider/model/transport are locked before the sample page and never silently changed mid-deck.

- [ ] **Step 2: Update Phase 4**

Document exact lock commands:

```bash
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider agy --transport native
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider codex --transport native
python scripts/plan_tool.py design --palette orange-teal --style glass-3d \
  --provider gemini --transport api
```

Require a capability/credential preflight before writing the lock.

- [ ] **Step 3: Update Phase 5–6 native worker instructions**

For AGY, each worker calls `generate_image` with a unique page-based image name and 16:9 ratio, then imports the returned file:

```bash
python scripts/gen_image.py --page P01 --provider agy --transport native \
  --import-file /absolute/path/to/agy/output.jpg --no-state
```

For Codex, each worker calls native `image_gen` and imports/finalizes the result with the equivalent `codex/native` command. Other clients continue to call `gen_image.py --provider gemini --transport api --no-state`.

- [ ] **Step 4: Update README and directory map**

Update the release number, highlights, routing table, stable Gemini model, AGY installation path `~/.agents/skills/ppt-creator/`, explicit bridge warning, migration note, no-mixing rule, new `image_providers.py`, and tests directory.

- [ ] **Step 5: Add behavior evaluations**

Add four evals asserting:

- AGY uses native `generate_image` and Nano Banana 2 without asking for a Google API key.
- Codex uses native `image_gen`, not AGY CLI.
- Another client requires Gemini API credentials and stable Flash model.
- A provider failure does not silently switch or mix the remaining pages.

- [ ] **Step 6: Validate documentation consistency**

Run:

```bash
rg -n "2\\.1\\.1|gemini-3\\.1-flash-image-preview|Codex 默认优先|默认 Codex 优先" .
python -m json.tool evals/evals.json >/dev/null
python scripts/validate_design.py
```

Expected: the search returns no stale production references; JSON and design validation succeed.

- [ ] **Step 7: Commit**

```bash
git add SKILL.md README.md references/phases/phase4-design.md \
  references/phases/phase5-6-generation.md evals/evals.json
git commit -m "docs: release host-native image routing v2.2.0"
```

### Task 5: Release Verification, GitHub Push, and Local Skill Sync

**Files:**
- Verify all repository files.
- Update installed copies:
  - `/Users/sunshuo/.codex/skills/ppt-creator/`
  - `/Users/sunshuo/.agents/skills/ppt-creator/`

- [ ] **Step 1: Run complete release checks**

Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_design.py
python -m json.tool evals/evals.json >/dev/null
git diff --check
git status --short --branch
```

Expected: tests and validators pass; no uncommitted implementation files remain.

- [ ] **Step 2: Review release diff and commit any final corrections**

Run:

```bash
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD
git diff origin/main..HEAD -- README.md SKILL.md scripts references/phases tests evals
```

Expected: only the approved v2.2.0 design, implementation, tests, and documentation are present.

- [ ] **Step 3: Push GitHub main**

Run: `git push origin main`  
Expected: GitHub accepts all v2.2.0 commits and local `main` matches `origin/main`.

- [ ] **Step 4: Synchronize the two installed Skills**

After the push succeeds, copy the repository release files into both installed skill directories while excluding `.git`, `docs/superpowers`, test caches, and generated workspaces. Preserve no stale v2.1.1 files.

- [ ] **Step 5: Verify local copies against GitHub release**

Check both installed `SKILL.md` files report v2.2.0. Compare recursive hashes for the runtime release set (`SKILL.md`, `README.md`, `scripts`, `references`, `evals`, `requirements.txt`, `LICENSE`) between the repository and each installed copy.

Expected: both comparisons report zero differences.

- [ ] **Step 6: Verify installed behavior**

Run the unit tests once against the repository and run `plan_tool.py --help` plus `gen_image.py --help` from each installed path.

Expected: both local installations expose AGY/Codex/Gemini provider options and native import arguments without errors.

### Task 6: Post-Release Style and Palette Research

**Files:**
- Read only:
  - `/Users/sunshuo/.codex/skills/huashu-design/SKILL.md`
  - `/Users/sunshuo/.codex/skills/guizang-ppt-skill/SKILL.md`
  - `/Users/sunshuo/.codex/skills/ppt-master/SKILL.md`
  - `references/design/INDEX.md`
  - `references/design/compatibility.json`

- [ ] **Step 1: Read all three comparison skill instructions**

Identify their reusable visual patterns, palette systems, layout grammar, audience fit, and any design-quality gates.

- [ ] **Step 2: Compare against the six current styles and six palettes**

Separate genuinely new visual systems from aliases or small variations of existing `flat-editorial`, `card-modern`, `glass-3d`, `illust-2.5d`, `lineart-minimal`, and `hud-frame`.

- [ ] **Step 3: Produce recommendations only**

Recommend candidate style and palette additions with:

- proposed ID and Chinese name;
- visual language and suitable scenarios;
- how it differs from existing options;
- compatible, conditional, and blocked combinations;
- reference-image needs and implementation priority.

Do not edit palette files, style files, `INDEX.md`, or `compatibility.json`.

- [ ] **Step 4: Deliver final release report**

Report the GitHub commit, push status, local AGY/Codex sync verification, test results, and the style/color recommendations.
