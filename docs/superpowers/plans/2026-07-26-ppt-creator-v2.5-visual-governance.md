# PPT Creator v2.5 Visual Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v2.5.0 with truthful visual compatibility, contrast-safe semantic text,
deck-rhythm preflight, neutral reference assets, one evidence-led style, and one restrained
technology palette.

**Architecture:** Keep the v2.4 plan contract and four-layer prompt flow. Add one governance
profile for single-dimension policies, extend the compatibility cross-product, and share a
small Python governance module between prompt generation, CLI preflight, plan locking, and
the build gate. Generate reference images deterministically and validate them by manifest.

**Tech Stack:** Python 3, unittest, Pillow, Markdown/JSON skill resources, Git worktrees.

---

### Task 1: Lock release invariants with failing design-system tests

**Files:**
- Modify: `tests/test_design_system.py`
- Test: `tests/test_design_system.py`

- [ ] Add a release test that expects v2.5.0, 12 palettes, 9 styles, 108 combinations,
  governance metadata, and eval IDs 25–32.
- [ ] Add assertions for corrected combinations and a maximum of three recommended styles
  per palette.
- [ ] Add a test that removes `{FOCUS_TEXT}` from a copied palette and expects validation
  to report the missing token.
- [ ] Add a test that changes `{FOCUS_TEXT}` to a low-contrast value and expects a contrast
  failure.
- [ ] Run `python3 -m unittest tests.test_design_system -v` and confirm failures are caused
  by missing v2.5 resources, not syntax mistakes.

### Task 2: Implement governance metadata and design validation

**Files:**
- Create: `references/design/governance.json`
- Modify: `references/design/compatibility.json`
- Modify: `scripts/validate_design.py`
- Modify: `references/design/palettes/*.md`
- Create: `references/design/palettes/graphite-cobalt.md`

- [ ] Add tier, shape, radius, shadow, density, image, annotation, material, and reference
  policies for all palettes and styles.
- [ ] Extend valid statuses to `recommended/allowed/specialized/legacy/blocked`.
- [ ] Require explanations for specialized and legacy entries; require alternatives for
  legacy and blocked entries.
- [ ] Add hex parsing, sRGB luminance, and 4.5:1 text-role contrast checks.
- [ ] Add four text-safe roles to every palette and create `graphite-cobalt`.
- [ ] Register all 12 × 9 combinations and audited contradiction corrections.
- [ ] Run `python3 -m unittest tests.test_design_system -v`; keep implementation minimal
  until this task is green.
- [ ] Run `python3 scripts/validate_design.py` and commit.

### Task 3: Add plan-level visual preflight with TDD

**Files:**
- Create: `tests/test_design_governance.py`
- Create: `scripts/design_governance.py`
- Create: `scripts/verify_design_plan.py`
- Modify: `scripts/plan_tool.py`
- Modify: `scripts/build_ppt.py`
- Modify: `tests/test_plan_tool.py`
- Modify: `tests/test_build_ppt.py`

- [ ] Write failing tests for blocked-combination errors, specialized/legacy warnings,
  three-consecutive-layout warnings, repeated three-card warnings, and a clean core plan.
- [ ] Run the focused tests and confirm each desired behavior fails first.
- [ ] Implement structured findings and normalized layout-family detection.
- [ ] Implement the CLI with `--plan`, `--design`, `--strict`, and optional `--json`.
- [ ] Make `plan_tool.py design` print deliberate-choice warnings without blocking them.
- [ ] Add the hard design error gate to `build_ppt.py`.
- [ ] Run focused tests until green, then run the full suite and commit.

### Task 4: Inject style governance into prompts with TDD

**Files:**
- Modify: `tests/test_make_prompt.py`
- Modify: `scripts/make_prompt.py`
- Modify: `references/constraints.md`

- [ ] Write failing tests proving the prompt contains the selected style’s shape, radius,
  shadow, material, evidence, accent, micro-label, and deck-rhythm rules.
- [ ] Write a failing test proving `product-evidence × graphite-cobalt` resolves every token.
- [ ] Run `python3 -m unittest tests.test_make_prompt -v` and verify red.
- [ ] Add governance loading and a deterministic prompt block after the four visual layers.
- [ ] Add global rules forbidding focus/status fill colors as small text and repeated
  generic three-card layouts.
- [ ] Re-run focused and full tests, then commit.

### Task 5: Add Product Evidence and neutralize style guidance

**Files:**
- Create: `references/design/styles/product-evidence.md`
- Modify: `references/design/styles/card-modern.md`
- Modify: `references/design/styles/flat-editorial.md`
- Modify: `references/design/styles/glass-3d.md`
- Modify: `references/design/styles/hud-frame.md`
- Modify: `references/design/styles/illust-2.5d.md`
- Modify: `references/design/styles/lineart-minimal.md`
- Modify: `references/design/styles/industrial-diagram.md`
- Modify: `references/design/styles/swiss-grid.md`

- [ ] Add the evidence-led style skeleton and page variants.
- [ ] Remove named-client provenance and obsolete default patterns from legacy template
  sections.
- [ ] Replace three-equal-card, fake-metric, version-label, generic robot/brain/chip, and
  decorative-English-micro-label examples with asymmetric, content-bound alternatives.
- [ ] Keep old template compatibility blocks but make them comply with current constraints.
- [ ] Run design validation and prompt tests, then commit.

### Task 6: Rebuild and validate all reference images

**Files:**
- Create: `tests/test_reference_assets.py`
- Create: `scripts/generate_style_refs.py`
- Create: `references/design/reference-manifest.json`
- Replace: `references/design/styles/{card-modern,flat-editorial,glass-3d,hud-frame,illust-2.5d,lineart-minimal}/ref-*.jpg`
- Create: `references/design/styles/product-evidence/ref-*.jpg`

- [ ] Write failing tests for exact manifest coverage, 1600×900 dimensions, no EXIF,
  SHA-256 integrity, and neutral-reference governance claims.
- [ ] Run the focused test and verify it fails before the generator exists.
- [ ] Implement deterministic Pillow compositions with no text-rendering calls.
- [ ] Generate 21 images and the manifest.
- [ ] Run `python3 scripts/generate_style_refs.py --check`,
  `python3 scripts/validate_design.py`, and focused tests.
- [ ] Visually inspect a contact sheet of all 21 images for branding, fake data, text,
  color dominance, and repeated three-card layouts; fix and regenerate if needed.
- [ ] Commit generated assets and generator together.

### Task 7: Update skill instructions, reference docs, and evals

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `references/design/INDEX.md`
- Modify: `references/phases/phase4-design.md`
- Modify: `references/phases/phase5-6-generation.md`
- Modify: `references/phases/phase7-assembly.md`
- Modify: `evals/evals.json`

- [ ] Update version/counts and explain tier meanings without adding a confirmation point.
- [ ] Document `graphite-cobalt`, `product-evidence`, text-safe roles, reference hygiene,
  and `verify_design_plan.py`.
- [ ] Add the visual preflight before sample generation and before assembly.
- [ ] Attribute transferred recommendations to Taste, 花叔 Design, 归藏 PPT Skill, and
  PPT Master while documenting what was not copied.
- [ ] Add evals 25–32 for legacy warning, evidence visuals, contrast-safe text, repeated
  layout, material conflict, shape lock, and neutral references.
- [ ] Keep SKILL.md under 500 lines and remove duplicated detail in favor of references.
- [ ] Run release-contract tests and commit.

### Task 8: Full verification and branch completion

**Files:**
- Verify all changed files

- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Run `python3 scripts/validate_design.py`.
- [ ] Run `python3 scripts/generate_style_refs.py --check`.
- [ ] Run the system `quick_validate.py` against the worktree.
- [ ] Run `python3 -m py_compile` for all scripts with cache redirected to `/tmp`.
- [ ] Review `git diff --check`, `git status`, version strings, counts, and release checklist.
- [ ] Merge the feature branch into `main`, repeat the full verification on merged `main`,
  and push `main` to GitHub.
- [ ] Install the exact pushed tree into `~/.codex/skills/ppt-creator` and
  `~/.agents/skills/ppt-creator`, preserving v2.4 backups.
- [ ] Diff both installations against the pushed tree and run quick validation plus the
  full test suite from each installation.

