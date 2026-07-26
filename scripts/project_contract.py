#!/usr/bin/env python3
"""Project contract schema normalization shared by PPT Creator scripts."""


ASSURANCE_PROFILES = {"standard", "client-facing", "evidence-sensitive"}
DELIVERY_MODES = {"raster_slide"}
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
    return validate_plan(plan)

