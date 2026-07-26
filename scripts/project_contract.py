#!/usr/bin/env python3
"""Project contract schema normalization shared by PPT Creator scripts."""

import hashlib
import json


ASSURANCE_PROFILES = {"standard", "client-facing", "evidence-sensitive"}
DELIVERY_MODES = {"raster_slide"}
PAGE_STATUS = [
    "pending",
    "prompted",
    "generating",
    "generated",
    "qa_passed",
    "approved",
]
CONTRACT_COLLECTIONS = (
    ("requirements", "requirement_refs"),
    ("claim_constraints", "claim_refs"),
    ("source_registry", "source_refs"),
)
PAGE_DEFAULTS = {
    "requirement_refs": list,
    "claim_refs": list,
    "source_refs": list,
    "asset_provenance": list,
    "evidence_level": lambda: None,
    "provenance_label": str,
    "reused_from": lambda: None,
    "reuse_mode": lambda: None,
    "dirty_reasons": list,
    "prompt_input_hash": lambda: None,
    "image_input_hash": lambda: None,
}


class ContractError(ValueError):
    """Raised when plan.json contains an invalid project contract."""


def _ensure_list(value, label):
    if not isinstance(value, list):
        raise ContractError(f"{label} 必须是数组")
    return value


def _contract_ids(plan):
    seen = {}
    for collection, _refs_field in CONTRACT_COLLECTIONS:
        for item in _ensure_list(plan.get(collection, []), collection):
            if not isinstance(item, dict):
                raise ContractError(f"{collection} 中的条目必须是对象")
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                raise ContractError(f"{collection} 条目缺少有效 id")
            if item_id in seen:
                raise ContractError(
                    f"项目契约 id 重复：{item_id} 同时出现在 "
                    f"{seen[item_id]} 和 {collection}"
                )
            seen[item_id] = collection
    return seen


def _page_index(plan):
    pages = _ensure_list(plan.get("pages", []), "pages")
    index = {}
    for page in pages:
        if not isinstance(page, dict):
            raise ContractError("pages 中的条目必须是对象")
        page_id = page.get("id")
        if not isinstance(page_id, str) or not page_id.strip():
            raise ContractError("页面缺少有效 id")
        if page_id in index:
            raise ContractError(f"页面 id 重复：{page_id}")
        index[page_id] = page
    return index


def _validate_reuse(page_index):
    for page_id, page in page_index.items():
        source_id = page.get("reused_from")
        mode = page.get("reuse_mode")
        if source_id is None:
            if mode is not None:
                raise ContractError(
                    f"页面 {page_id} 设置了 reuse_mode 但没有 reused_from"
                )
            continue
        if mode != "exact_asset":
            raise ContractError(
                f"页面 {page_id} 的 reuse_mode 必须是 exact_asset"
            )
        if source_id == page_id:
            raise ContractError(f"页面 {page_id} 不得复用自身")
        if source_id not in page_index:
            raise ContractError(
                f"页面 {page_id} 的复用来源不存在：{source_id}"
            )

    visiting = set()
    visited = set()

    def visit(page_id):
        if page_id in visiting:
            raise ContractError(f"页面复用关系存在循环：{page_id}")
        if page_id in visited:
            return
        visiting.add(page_id)
        source_id = page_index[page_id].get("reused_from")
        if source_id:
            visit(source_id)
        visiting.remove(page_id)
        visited.add(page_id)

    for page_id in page_index:
        visit(page_id)


def validate_plan(plan):
    """Validate contract IDs, page references, delivery mode, and reuse graph."""
    profile = plan.get("assurance_profile")
    if profile not in ASSURANCE_PROFILES:
        allowed = ", ".join(sorted(ASSURANCE_PROFILES))
        raise ContractError(
            f"assurance_profile '{profile}' 不受支持；可选：{allowed}"
        )
    delivery_mode = plan.get("delivery_mode")
    if delivery_mode not in DELIVERY_MODES:
        allowed = ", ".join(sorted(DELIVERY_MODES))
        raise ContractError(
            f"delivery_mode '{delivery_mode}' 不受支持；当前可选：{allowed}"
        )

    contract_ids = _contract_ids(plan)
    page_index = _page_index(plan)
    for page_id, page in page_index.items():
        for collection, refs_field in CONTRACT_COLLECTIONS:
            refs = _ensure_list(page.get(refs_field, []), f"{page_id}.{refs_field}")
            for ref in refs:
                if ref not in contract_ids:
                    raise ContractError(
                        f"页面 {page_id} 引用了不存在的 {collection} id：{ref}"
                    )
                if contract_ids[ref] != collection:
                    raise ContractError(
                        f"页面 {page_id} 的 {refs_field} 错误引用了 "
                        f"{contract_ids[ref]} id：{ref}"
                    )
        _ensure_list(
            page.get("asset_provenance", []),
            f"{page_id}.asset_provenance",
        )
        _ensure_list(page.get("dirty_reasons", []), f"{page_id}.dirty_reasons")
    _validate_reuse(page_index)
    return plan


def normalize_plan(plan):
    """Add v2.4 defaults in place while preserving all existing fields."""
    if not isinstance(plan, dict):
        raise ContractError("plan.json 顶层必须是对象")
    plan.setdefault("schema_version", "2.4")
    plan.setdefault("assurance_profile", "standard")
    plan.setdefault("delivery_mode", "raster_slide")
    plan.setdefault("requirements", [])
    plan.setdefault("claim_constraints", [])
    plan.setdefault("source_registry", [])
    for page in plan.get("pages", []):
        for field, factory in PAGE_DEFAULTS.items():
            if field not in page:
                page[field] = factory()
    validate_plan(plan)
    adopt_legacy_hashes(plan)
    return plan


def page_index(plan):
    """Return pages by ID after validating the normalized plan."""
    return {page["id"]: page for page in plan.get("pages", [])}


def applicable_entries(plan, page, collection, refs_field):
    """Resolve explicit page references plus global/page-scoped contract entries."""
    refs = set(page.get(refs_field, []))
    applicable = []
    for item in plan.get(collection, []):
        affected = item.get("affected_pages")
        if (
            item["id"] in refs
            or not affected
            or "all" in affected
            or page["id"] in affected
        ):
            applicable.append(item)
    return applicable


def _visible_text(page):
    values = [
        page.get("title", ""),
        page.get("subtitle", ""),
        *page.get("points", []),
        page.get("layout_hint", ""),
    ]
    return "\n".join(str(value) for value in values if value)


def _finding(severity, page_id, rule_id, message):
    return {
        "severity": severity,
        "page": page_id,
        "rule_id": rule_id,
        "message": message,
    }


def _lint_rule_text(
    page, rule, visible_text, all_text, required_severity="error"
):
    findings = []
    rule_id = rule["id"]
    for term in rule.get("required_terms", []):
        if term and term not in visible_text:
            findings.append(
                _finding(
                    required_severity,
                    page["id"],
                    rule_id,
                    f"缺少必需词：{term}",
                )
            )
    for term in rule.get("forbidden_terms", []):
        if term and term in all_text:
            findings.append(
                _finding(
                    "error",
                    page["id"],
                    rule_id,
                    f"命中禁止词：{term}",
                )
            )
    return findings


def lint_pages(plan, page_ids=None, text_overrides=None, strict=False):
    """Return structured semantic findings for plan text or supplied OCR text."""
    normalize_plan(plan)
    wanted = set(page_ids) if page_ids is not None else None
    overrides = text_overrides or {}
    findings = []
    for page in plan.get("pages", []):
        if wanted is not None and page["id"] not in wanted:
            continue
        visible_text = overrides.get(page["id"], _visible_text(page))
        required_severity = (
            "error"
            if page["id"] not in overrides or strict
            else "warning"
        )
        all_text = visible_text
        if page["id"] not in overrides and page.get("notes"):
            all_text += "\n" + page["notes"]
        for rule in applicable_entries(
            plan, page, "requirements", "requirement_refs"
        ):
            findings.extend(
                _lint_rule_text(
                    page,
                    rule,
                    visible_text,
                    all_text,
                    required_severity=required_severity,
                )
            )
        for rule in applicable_entries(
            plan, page, "claim_constraints", "claim_refs"
        ):
            findings.extend(
                _lint_rule_text(
                    page,
                    rule,
                    visible_text,
                    all_text,
                    required_severity=required_severity,
                )
            )

        is_case = (
            page.get("page_type") == "case"
            or page.get("template") == "case"
        )
        if not is_case:
            continue
        profile = plan["assurance_profile"]
        evidence = page.get("evidence_level")
        if profile == "client-facing" and not evidence:
            findings.append(
                _finding(
                    "warning",
                    page["id"],
                    "ASSURANCE-EVIDENCE",
                    "客户案例页尚未声明 evidence_level",
                )
            )
        if profile == "evidence-sensitive":
            if not evidence:
                findings.append(
                    _finding(
                        "error",
                        page["id"],
                        "ASSURANCE-EVIDENCE",
                        "证据敏感型案例页必须声明 evidence_level",
                    )
                )
            elif evidence == "verified" and not page.get("source_refs"):
                findings.append(
                    _finding(
                        "error",
                        page["id"],
                        "ASSURANCE-SOURCE",
                        "verified 案例页必须引用至少一个来源",
                    )
                )
            elif evidence == "conceptual" and not page.get(
                "provenance_label", ""
            ).strip():
                findings.append(
                    _finding(
                        "error",
                        page["id"],
                        "ASSURANCE-PROVENANCE",
                        "conceptual 案例页必须提供可见的 provenance_label",
                    )
                )
    return findings


def format_findings(findings):
    """Render semantic findings for CLI output."""
    return "\n".join(
        f"[{item['severity'].upper()}] {item['page']} "
        f"{item['rule_id']}: {item['message']}"
        for item in findings
    )


def prompt_contract_block(plan, page):
    """Build a source-path-free project contract fragment for image prompts."""
    entries = applicable_entries(
        plan, page, "requirements", "requirement_refs"
    ) + applicable_entries(
        plan, page, "claim_constraints", "claim_refs"
    )
    lines = []
    for item in entries:
        wording = item.get("decision") or item.get("rule")
        if wording:
            lines.append(f"- {item['id']}: {wording}")
    if page.get("evidence_level"):
        lines.append(f"- Evidence level: {page['evidence_level']}")
    if page.get("provenance_label"):
        lines.append(
            "- Visible provenance label (exact text): "
            + page["provenance_label"]
        )
    if not lines:
        return ""
    return "PROJECT CONTRACT (must follow exactly):\n" + "\n".join(lines)


def stable_hash(value):
    """Hash JSON-compatible data deterministically."""
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sorted_entries(entries):
    return sorted(entries, key=lambda item: item["id"])


def expected_page_hash(plan, page_or_id, _stack=None):
    """Hash every project input that can change a page's visible artifact."""
    pages = page_index(plan)
    page = (
        pages[page_or_id]
        if isinstance(page_or_id, str)
        else page_or_id
    )
    stack = list(_stack or [])
    if page["id"] in stack:
        raise ContractError(f"页面复用关系存在循环：{page['id']}")
    stack.append(page["id"])

    requirements = _sorted_entries(
        applicable_entries(
            plan, page, "requirements", "requirement_refs"
        )
    )
    claims = _sorted_entries(
        applicable_entries(
            plan, page, "claim_constraints", "claim_refs"
        )
    )
    source_ids = set(page.get("source_refs", []))
    sources = _sorted_entries(
        [
            source
            for source in plan.get("source_registry", [])
            if source["id"] in source_ids
        ]
    )
    payload = {
        "assurance_profile": plan.get("assurance_profile", "standard"),
        "delivery_mode": plan.get("delivery_mode", "raster_slide"),
        "design": {
            key: plan.get(key)
            for key in (
                "palette",
                "style",
                "industry",
                "provider",
                "image_transport",
                "image_model",
            )
        },
        "page": {
            key: page.get(key)
            for key in (
                "template",
                "page_type",
                "title",
                "subtitle",
                "points",
                "layout_hint",
                "requirement_refs",
                "claim_refs",
                "source_refs",
                "evidence_level",
                "provenance_label",
                "asset_provenance",
                "reused_from",
                "reuse_mode",
            )
        },
        "requirements": requirements,
        "claim_constraints": claims,
        "sources": sources,
    }
    source_id = page.get("reused_from")
    if source_id:
        payload["reused_source_hash"] = expected_page_hash(
            plan, source_id, stack
        )
    return stable_hash(payload)


def _status_at_least(page, minimum):
    status = page.get("status", "pending")
    try:
        return PAGE_STATUS.index(status) >= PAGE_STATUS.index(minimum)
    except ValueError as exc:
        raise ContractError(
            f"页面 {page.get('id', '?')} 状态无效：{status}"
        ) from exc


def adopt_legacy_hashes(plan):
    """Adopt current inputs for pre-v2.4 pages that have no tracking hashes."""
    for page in plan.get("pages", []):
        current = expected_page_hash(plan, page)
        if (
            _status_at_least(page, "prompted")
            and not page.get("prompt_input_hash")
        ):
            page["prompt_input_hash"] = current
        if (
            _status_at_least(page, "generated")
            and not page.get("image_input_hash")
        ):
            page["image_input_hash"] = current
    return plan


def record_prompt_hash(plan, page_or_id):
    """Record that a prompt reflects the page's current project inputs."""
    page = (
        page_index(plan)[page_or_id]
        if isinstance(page_or_id, str)
        else page_or_id
    )
    page["prompt_input_hash"] = expected_page_hash(plan, page)
    page["dirty_reasons"] = []
    return page["prompt_input_hash"]


def record_image_hash(plan, page_or_id):
    """Record that a generated image reflects the page's current inputs."""
    page = (
        page_index(plan)[page_or_id]
        if isinstance(page_or_id, str)
        else page_or_id
    )
    current = expected_page_hash(plan, page)
    page["prompt_input_hash"] = page.get("prompt_input_hash") or current
    page["image_input_hash"] = current
    page["dirty_reasons"] = []
    return current


def sync_findings(plan):
    """Report pages whose tracked prompt/image inputs are no longer current."""
    normalize_plan(plan)
    findings = []
    for page in plan.get("pages", []):
        current = expected_page_hash(plan, page)
        mismatch = bool(page.get("dirty_reasons"))
        if (
            _status_at_least(page, "prompted")
            and page.get("prompt_input_hash") != current
        ):
            mismatch = True
        if (
            _status_at_least(page, "generated")
            and page.get("image_input_hash") != current
        ):
            mismatch = True
        if mismatch:
            findings.append(
                {
                    "page": page["id"],
                    "reason": "project_input_changed",
                }
            )
    return findings


def invalidate_stale_pages(plan, reason="project_input_changed"):
    """Reset only pages whose current inputs no longer match tracked artifacts."""
    normalize_plan(plan)
    stale_ids = {item["page"] for item in sync_findings(plan)}
    changed = []
    for page in plan.get("pages", []):
        if page["id"] not in stale_ids:
            continue
        page["status"] = "pending"
        if reason not in page["dirty_reasons"]:
            page["dirty_reasons"].append(reason)
        page["prompt_input_hash"] = None
        page["image_input_hash"] = None
        changed.append(page["id"])
    return changed


def effective_page(plan, page_or_id):
    """Resolve an exact-asset alias to its visible source page."""
    pages = page_index(plan)
    page = (
        pages[page_or_id]
        if isinstance(page_or_id, str)
        else page_or_id
    )
    while page.get("reused_from"):
        page = pages[page["reused_from"]]
    return page


def effective_image(plan, page_or_id):
    """Return the image path actually used for a page or exact alias."""
    source = effective_page(plan, page_or_id)
    return source["image"]


def render_outline(plan):
    """Render the canonical Markdown view of the current page plan."""
    normalize_plan(plan)
    lines = [
        "<!-- Generated by PPT Creator v2.4; do not edit. -->",
        f"# {plan.get('topic') or '未命名演示文稿'}",
        "",
        f"- 受众：{plan.get('audience') or '未指定'}",
        f"- 保障级别：{plan['assurance_profile']}",
        f"- 交付模式：{plan['delivery_mode']}",
        "",
        "## 逐页大纲",
    ]
    for page in plan.get("pages", []):
        lines.extend(["", f"### {page['id']} {page.get('title', '')}"])
        if page.get("subtitle"):
            lines.extend(["", f"- 副标题：{page['subtitle']}"])
        for point in page.get("points", []):
            if len(lines) == 0 or lines[-1] != "":
                if lines[-1].startswith("### "):
                    lines.append("")
            lines.append(f"- {point}")
    return "\n".join(lines).rstrip() + "\n"


def export_outline(plan, path):
    """Write the generated outline and return its path."""
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_outline(plan), encoding="utf-8")
    return target
