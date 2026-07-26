# PPT Creator v2.4 Project Contract & Sync Design

## Goal

Upgrade PPT Creator from page-status tracking to a generic, verifiable project contract that
preserves user decisions, claim boundaries, evidence provenance, reuse relationships, and artifact
freshness across revisions without adding user confirmation points or industry-specific rules.

## Scope

This release includes:

- three assurance profiles: `standard`, `client-facing`, and `evidence-sensitive`;
- structured requirements, claim constraints, and source registry entries;
- page-level rule/source references, evidence metadata, and exact asset reuse;
- deterministic content hashes and automatic invalidation of stale pages;
- pre-generation semantic lint and an optional OCR-text verification adapter;
- generated outline, final synchronization gate, and a minimal delivery manifest;
- automatic compatibility normalization for v2.3 plans;
- documentation, unit tests, cross-industry evals, and release version updates.

This release does not include:

- editable-native or hybrid PowerPoint rendering;
- a mandatory OCR engine or OCR network service;
- generation cost accounting or provider token estimation;
- new palettes, styles, page types, or industry content rules;
- additional user confirmation points or additional numbered workflow phases.

## Architecture

Keep `plan.json` as the canonical current-state manifest, but do not turn it into an append-only
database. Store only current decisions, references, hashes, and page status there. Generated outline,
semantic reports, delivery manifests, and future operational logs remain sidecar artifacts.

Add `scripts/project_contract.py` as the single reusable implementation boundary for:

- schema normalization and validation;
- applicable-rule/source resolution;
- deterministic page-input hashing;
- stale-state detection and propagation;
- semantic lint;
- exact reuse resolution;
- generated outline and manifest data.

`plan_tool.py`, `make_prompt.py`, `verify_semantics.py`, `verify_pages.py`, `gen_image.py`, and
`build_ppt.py` call that module instead of duplicating contract logic.

## Contract Schema

New plans use `schema_version: "2.4"` and default to:

```json
{
  "assurance_profile": "standard",
  "delivery_mode": "raster_slide",
  "requirements": [],
  "claim_constraints": [],
  "source_registry": []
}
```

Requirement and claim entries use stable IDs and generic checks:

```json
{
  "id": "REQ-TECH-001",
  "decision": "Use the approved platform name",
  "required_terms": ["Harness"],
  "forbidden_terms": ["Hermes"],
  "affected_pages": ["P01", "P05"]
}
```

Page entries may add:

```json
{
  "requirement_refs": ["REQ-TECH-001"],
  "claim_refs": [],
  "source_refs": ["SRC-001"],
  "evidence_level": "conceptual",
  "provenance_label": "方案示意",
  "asset_provenance": [
    {"asset": "hero_image", "type": "ai_generated"}
  ],
  "reused_from": null,
  "dirty_reasons": [],
  "prompt_input_hash": null,
  "image_input_hash": null
}
```

Unknown optional fields remain untouched for forward compatibility.

## Assurance Profiles

- `standard`: project rules are enforced when supplied; sources and evidence labels are optional.
- `client-facing`: project rules are enforced; case pages without evidence metadata produce warnings.
- `evidence-sensitive`: case pages must declare an evidence level; verified claims require source
  references; conceptual cases require a visible provenance label.

Profiles change validation strictness only. They never inject industry content.

## Change Propagation

Compute a canonical SHA-256 input hash for each page from:

- image-visible page content and layout;
- applicable requirement and claim entries;
- referenced sources and provenance metadata;
- locked palette, style, industry, provider, transport, and model;
- exact-reuse ancestry.

Do not use filesystem modification time. When the expected hash differs from the stored prompt or
image input hash:

- set the affected page back to `pending`;
- record a stable `dirty_reasons` value;
- clear obsolete prompt/image hashes;
- propagate invalidation to exact-reuse descendants;
- leave unrelated pages untouched.

Legacy v2.3 pages without hashes adopt their current state on first normalization so existing work
does not become stale merely because the Skill was upgraded.

## Semantic Validation

Before prompt generation and final build:

- block forbidden terms;
- require configured exact terms on affected pages;
- validate referenced rule/source IDs;
- enforce the selected assurance profile;
- reject unsupported delivery modes.

After page generation, `verify_semantics.py` consumes optional UTF-8 OCR text files. It always blocks
detected forbidden terms. Missing titles, required terms, and expected numbers are warnings by
default and become errors with `--strict`. Missing OCR is skipped unless `--require-ocr` is set.

## Page Reuse

Support `reuse_mode: "exact_asset"` with `reused_from`. Validate that:

- the source page exists;
- a page cannot reuse itself;
- reuse relationships contain no cycles;
- reused pages do not generate independent prompts or images;
- verification and assembly resolve the source image;
- changes to a source invalidate all descendants.

Speaker notes remain page-specific even when the visible image is reused.

## Workflow Integration

- Phase 1–3: select an assurance profile, capture the project contract, and initialize page refs.
- Phase 4: retain the existing four-layer visual lock.
- Phase 5–6: run exact lint before prompts; use optional OCR semantic verification after generation.
- Phase 7: run page verification, semantic lint, synchronization check, generated-outline export,
  build, and delivery-manifest generation.

No additional numbered phases or user confirmations are introduced.

## Compatibility and Failure Handling

- Normalize v2.3 plans in memory and preserve all unknown fields.
- Fail with actionable messages for duplicate IDs, missing refs, invalid assurance profiles,
  unsupported delivery modes, reuse cycles, semantic violations, or stale approved pages.
- Keep OCR optional and dependency-free.
- Never write API keys, credentials, or source document contents into logs or manifests.

## Verification

Automated tests cover:

- legacy-plan migration;
- profile-specific source/provenance rules;
- exact required/forbidden term lint;
- page-only and global invalidation;
- design/provider changes invalidating all pages;
- exact-reuse validation and propagation;
- prompt hash recording;
- native/script generation hash recording;
- optional OCR warning/error behavior;
- generated outline consistency;
- final build refusal for stale content;
- manifest contents;
- port, finance, manufacturing, and general scenarios.

