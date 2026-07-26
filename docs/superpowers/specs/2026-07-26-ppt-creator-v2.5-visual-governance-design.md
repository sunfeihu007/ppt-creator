# PPT Creator v2.5 Visual Governance Design

## 1. Goal

Release PPT Creator v2.5.0 as a visual-governance upgrade. Preserve the existing seven
phases, project contract, raster-slide delivery, image-provider routing, and four-layer
visual model. Improve only the style and color system:

- retire unsafe, branded, fake-data reference imagery;
- make palette and material compatibility truthful;
- distinguish core, conditional, specialized, brand, and legacy choices;
- make text-on-background contrast machine-checkable;
- detect repetitive deck rhythm before generation;
- add one missing evidence-led style and one restrained general-technology palette.

## 2. Critical review of the earlier recommendation

The previous audit mixed transferable design principles with Web-only rules. v2.5 adopts
only the parts that improve static 16:9 presentation decks:

- audit before redesign;
- one focal accent per page;
- a locked shape/radius/shadow system across the deck;
- no default three-equal-card composition;
- no fake precision, fake logos, or fake screenshots;
- no repeated layout family for three consecutive pages;
- real/source-backed visual evidence before decorative illustration;
- WCAG-style contrast checks for text tokens.

The following Taste rules are explicitly out of scope:

- motion, hover, responsive breakpoints, mobile collapse, navigation, CTA, forms;
- frontend framework, icon package, dark-mode toggle, Core Web Vitals;
- a universal em-dash ban or marketing-copy rules unrelated to PPT rendering.

The earlier recommendation also proposed “design dials.” Exposing new user-facing plan
fields for variance and density would add schema and confirmation complexity without
proving value. v2.5 therefore stores bounded style policies in a machine profile and
injects them automatically. No new user confirmation point and no plan schema bump.

## 3. Release boundary

### Keep unchanged

- `plan.json` schema remains 2.4.
- `style × page_type × industry × palette` remains the visual architecture.
- Client brand still outranks company brand and industry defaults.
- Phase 4 locks one `palette × style × industry × provider` for the whole deck.
- Existing legal combinations remain loadable unless they contain a direct material
  contradiction; legacy choices produce warnings rather than silent removal.

### Add

- Skill release version: v2.5.0.
- 12 palettes, 9 styles, 108 explicit combinations.
- `graphite-cobalt` palette.
- `product-evidence` style.
- `references/design/governance.json`.
- `scripts/design_governance.py` and `scripts/verify_design_plan.py`.
- deterministic neutral reference-image generator and manifest.
- four text-safe semantic tokens for focus and status copy.

## 4. Machine architecture

### 4.1 Compatibility remains the cross-product authority

`references/design/compatibility.json` continues to list every palette × style pair.
Allowed statuses become:

- `recommended`: first-choice combination;
- `allowed`: compatible but not a default;
- `specialized`: use only when the requested visual device is deliberate;
- `legacy`: supported for existing decks but not proposed for new work;
- `blocked`: direct material or theme contradiction.

Each palette may have no more than three `recommended` styles. `blocked` requires a reason
and alternatives. `specialized` and `legacy` require an explanation; `legacy` requires a
modern alternative.

### 4.2 Governance profile owns single-dimension policy

`references/design/governance.json` contains:

- palette tier and theme;
- style tier, density range, variance range;
- shape, radius, shadow, image, annotation, and material rules;
- deck rules such as maximum consecutive layout-family repetition;
- reference mode and required neutral reference roles.

This avoids duplicating style policy across prompts and validators.

### 4.3 Prompt composition

`make_prompt.py` composes:

1. style skeleton;
2. registered page-type fragment;
3. industry visual fragment;
4. resolved palette tokens;
5. a generated deck-wide governance block;
6. exact page content;
7. project contract;
8. global constraints.

Flat styles explicitly flatten palette gradients. Glass and HUD remain material-specific
and are blocked from palettes that prohibit those materials.

## 5. Palette governance

### 5.1 Tiers

- Core: `orange-teal`, `finance-navy-teal`, `industrial-navy-orange`, `ink-paper`,
  `swiss-ikb`, `graphite-cobalt`.
- Brand-only: `liantong-red`.
- Conditional: `navy-gold`, `forest-ivory`.
- Specialized: `deep-space`.
- Legacy: `tech-blue`, `warm-orange`.

`graphite-cobalt` uses cold gray, graphite structure, and one cobalt focal color. It has
no visible gradient and becomes the neutral general-technology alternative to legacy
`tech-blue`. Company-branded work still defaults to `orange-teal`.

### 5.2 Text-safe roles

Every palette must define:

- `{FOCUS_TEXT}`;
- `{STATUS_OK_TEXT}`;
- `{STATUS_WARN_TEXT}`;
- `{STATUS_RISK_TEXT}`.

These roles are checked at 4.5:1 against both `{BACKGROUND}` and `{SURFACE}`. Existing
fill/line colors remain available but must not be used as small body text. Inverse text is
checked against inverse background.

## 6. Style governance

### 6.1 Tiers

- Core: `swiss-grid`, `industrial-diagram`, `flat-editorial`, `product-evidence`.
- Conditional: `lineart-minimal`, `card-modern`, `illust-2.5d`.
- Specialized: `glass-3d`, `hud-frame`.

### 6.2 Product Evidence

`product-evidence` is for product introductions, customer cases, demos, and solution proof:

- one source-backed screenshot, photo, diagram, or generated conceptual scene occupies
  55–70% of the page;
- a narrow annotation rail explains only provided facts;
- an evidence band names source/provenance when required;
- no div-like fake screenshot, fake customer logo, fake metric, or decorative device frame;
- conceptual imagery keeps the visible provenance label from the project contract.

## 7. Deck-rhythm preflight

`design_governance.lint_plan()` returns structured findings:

- error for blocked or unregistered combinations;
- warning for specialized/legacy selections;
- warning for three consecutive pages with the same normalized layout family;
- warning when three-equal-card/card-wall hints recur;
- warning when the selected palette or style is legacy/specialized.

`verify_design_plan.py` prints findings and can write JSON. Errors always fail. `--strict`
also fails on warnings. Phase 4 and Phase 7 call the default non-strict mode; deliberate
specialized choices therefore remain usable.

## 8. Reference-image reset

The 18 existing references are replaced by deterministic, text-free, brand-free,
data-free, palette-neutral images. Three new references are generated for
`product-evidence`. The generator:

- writes 1600×900 JPEGs without EXIF;
- uses neutral gray/graphite geometry and a restrained muted accent;
- never draws text, logos, version labels, dates, percentages, device brands, or people;
- writes SHA-256 values and semantic roles to `reference-manifest.json`.

The design validator verifies the manifest, dimensions, file set, hashes, and governance
claims. References are layout/material cues only; current palette tokens remain authoritative.

## 9. Compatibility corrections

At minimum, the matrix must encode these audited corrections:

- `orange-teal × lineart-minimal`: allowed;
- `tech-blue × lineart-minimal`: legacy, with flat-style material precedence;
- `swiss-ikb × glass-3d`: blocked;
- `finance-navy-teal × glass-3d`: blocked;
- `deep-space`: recommended only with `hud-frame`;
- `hud-frame`: blocked for all light palettes;
- no palette has more than three recommended styles.

## 10. Validation and release criteria

The release is complete only when:

- every new behavior has a red-green regression test;
- all 12 palette files pass semantic-token and contrast checks;
- all 9 style profiles and 108 combinations validate;
- all 21 generated references pass manifest validation;
- prompt tests prove governance injection and token resolution;
- plan preflight tests prove repetition and tier warnings;
- all existing tests still pass;
- `quick_validate.py` accepts the skill;
- feature branch is merged to `main`, pushed to GitHub, and both local Codex and AGY
  installations match the pushed tree.

