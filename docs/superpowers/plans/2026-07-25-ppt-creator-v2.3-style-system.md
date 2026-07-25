# PPT Creator v2.3 Visual System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade PPT Creator from a two-dimensional palette × style selector into a backward-compatible visual system that composes style family × page type × industry modifier × semantic palette.

**Architecture:** Keep the seven workflow phases and legacy `template` values. Add data-driven page-type and industry prompt fragments, normalize old plans to the new fields, and assemble prompts from four visual layers. Preserve the existing palette × style compatibility gate while extending it to the new palettes and styles.

**Tech Stack:** Python 3 standard library, Markdown/JSON design resources, `unittest`.

---

### Task 1: Lock the v2.3 visual data model

**Files:**
- Create: `references/design/page-types/index.json`
- Create: `references/design/page-types/*.md`
- Create: `references/design/industries/index.json`
- Create: `references/design/industries/*.md`

- [ ] **Step 1: Define the eleven canonical page types**

Create mappings for `cover`, `toc`, `section`, `overview`, `architecture`, `flow`, `detail`,
`compare-kpi`, `case`, `roadmap`, and `closing`. Map every legacy template to one canonical
type so old draft plans continue to work.

- [ ] **Step 2: Define four industry visual modifiers**

Create `general`, `port-terminal`, `finance`, and `automotive-manufacturing` prompt fragments.
Each fragment controls motifs, geometry, image treatment, icon treatment, and visual tone only;
it must not prescribe slide content.

- [ ] **Step 3: Add resource validation expectations**

Require every index entry to resolve to a Markdown file containing a fenced prompt fragment.

### Task 2: Expand the core style and palette library

**Files:**
- Create: `references/design/styles/swiss-grid.md`
- Create: `references/design/styles/industrial-diagram.md`
- Modify: `references/design/styles/*.md`
- Create: `references/design/palettes/finance-navy-teal.md`
- Create: `references/design/palettes/industrial-navy-orange.md`
- Create: `references/design/palettes/ink-paper.md`
- Create: `references/design/palettes/swiss-ikb.md`
- Create: `references/design/palettes/forest-ivory.md`
- Modify: `references/design/palettes/*.md`
- Modify: `references/design/compatibility.json`
- Modify: `references/design/INDEX.md`

- [ ] **Step 1: Add a deck-wide style skeleton to every style**

Add a `风格提示词骨架` fenced block that defines typography, grid, material, radius, line,
shadow, image, icon, and diagram rules independently of page content.

- [ ] **Step 2: Add the two approved core styles**

Implement `swiss-grid` as the general grid-led family and `industrial-diagram` as the
engineering/diagram-led family.

- [ ] **Step 3: Add semantic color roles**

Every palette must define `BACKGROUND`, `SURFACE`, `STRUCTURE`, `FOCUS`, `TEXT_PRIMARY`,
`TEXT_SECONDARY`, `BORDER`, `INVERSE_BACKGROUND`, `INVERSE_TEXT`, `STATUS_OK`,
`STATUS_WARN`, and `STATUS_RISK`. Keep legacy tokens for old custom templates.

- [ ] **Step 4: Add five approved palettes**

Add finance, industrial, ink-paper, Swiss IKB, and forest-ivory palettes with restrained
usage rules and accessible text-role colors.

- [ ] **Step 5: Register all combinations explicitly**

Expand the compatibility matrix from 6 × 6 to 11 × 8. Every blocked combination must have a
reason and useful alternatives.

### Task 3: Make plan.json understand visual layers

**Files:**
- Modify: `scripts/plan_tool.py`
- Modify: `tests/test_plan_tool.py`

- [ ] **Step 1: Write failing normalization tests**

Test that an old plan gains `industry: general` and canonical page types without losing legacy
fields. Test that `design --industry finance` locks the industry modifier.

- [ ] **Step 2: Implement backward-compatible normalization**

Load page-type mappings from the design index, normalize pages on load, persist new fields only
when writing, and reject unknown industries.

- [ ] **Step 3: Extend status output**

Show palette × style × industry together so a resumed task makes the complete visual lock clear.

- [ ] **Step 4: Run the focused tests**

Run `python3 -m unittest tests.test_plan_tool -v`; expect all plan tests to pass.

### Task 4: Compose prompts from four visual layers

**Files:**
- Modify: `scripts/make_prompt.py`
- Create: `tests/test_make_prompt.py`

- [ ] **Step 1: Write failing prompt-composition tests**

Verify that a legacy `arch` page resolves to `architecture`, the selected industry fragment is
included, semantic palette tokens are replaced, and style/page/industry placeholders do not
leak into the final prompt.

- [ ] **Step 2: Implement style-skeleton parsing**

Prefer the new deck-wide style skeleton. Retain the old page-template picker as a fallback for
third-party or older custom styles.

- [ ] **Step 3: Implement page-type and industry fragment loading**

Resolve the fragments through their indexes, append the exact page content afterwards, and then
append global constraints.

- [ ] **Step 4: Run the focused tests**

Run `python3 -m unittest tests.test_make_prompt -v`; expect all prompt tests to pass.

### Task 5: Strengthen design validation

**Files:**
- Modify: `scripts/validate_design.py`
- Create: `tests/test_design_system.py`

- [ ] **Step 1: Write failing validation tests**

Assert 11 palettes, 8 styles, 11 page types, 4 industries, semantic tokens on every palette,
style skeletons on every style, and valid default industry combinations.

- [ ] **Step 2: Implement resource validation**

Validate indexes, referenced files, fenced fragments, style skeletons, semantic tokens, and the
complete compatibility matrix.

- [ ] **Step 3: Run focused and CLI validation**

Run `python3 -m unittest tests.test_design_system -v` and
`python3 scripts/validate_design.py`; both must pass.

### Task 6: Update workflow instructions and user documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `references/phases/phase1-3-planning.md`
- Modify: `references/phases/phase4-design.md`
- Modify: `references/phases/phase5-6-generation.md`
- Modify: `references/constraints.md`
- Modify: `README.md`
- Modify: `evals/evals.json`

- [ ] **Step 1: Keep Phase 1–3 content planning unchanged**

Only document the canonical visual page type alongside the legacy `template`; do not add
industry-specific content planning.

- [ ] **Step 2: Update Phase 4**

Select palette, style, and visual-only industry modifier; preserve customer brand priority;
record the complete design lock before samples.

- [ ] **Step 3: Update the design sample**

Use one merged confirmation containing cover + architecture + detail/case whenever those page
types exist. This remains a single confirmation checkpoint.

- [ ] **Step 4: Update version and documentation**

Release as v2.3.0, document the four-layer visual system and new defaults, and add behavior evals
for page-type and industry-style routing.

### Task 7: Verify, review, and release the branch

**Files:**
- Validate: entire repository

- [ ] **Step 1: Run all automated checks**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_design.py
python3 /Users/sunshuo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Expected: all unit tests pass, the 11 × 8 matrix validates, and the Skill validator reports
`Skill is valid!`.

- [ ] **Step 2: Inspect the generated prompt**

Create a temporary plan for a finance architecture page, run `make_prompt.py --print`, and verify
that style, page type, industry, semantic palette, exact content, and constraints all appear in
the correct order with no unresolved placeholders.

- [ ] **Step 3: Review the diff**

Check that content-planning behavior is unchanged, no credentials or generated artifacts are
tracked, and only v2.3 visual-system files are modified.

- [ ] **Step 4: Commit the feature branch**

Commit the verified change with:

```bash
git add SKILL.md README.md evals references scripts tests docs
git commit -m "feat: add layered industry visual system for PPT Creator v2.3"
```
