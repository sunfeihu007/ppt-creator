#!/usr/bin/env python3
"""Manage plan.json, page QA, consolidated reviews, and workflow gates."""
import argparse
import json
import os
import sys
import tempfile

import project_contract

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
PLAN = os.path.join(WS, "plan.json")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(REPO, "references", "design")
COMPATIBILITY = os.path.join(DESIGN, "compatibility.json")
PAGE_TYPES_INDEX = os.path.join(DESIGN, "page-types", "index.json")
INDUSTRIES_INDEX = os.path.join(DESIGN, "industries", "index.json")
PHASES = ["1_outline", "2_content", "3_pages", "4_design",
          "5_framework", "6_content_pages", "7_assembly"]
PAGE_STATUS = ["pending", "prompted", "generating", "generated", "qa_passed", "approved"]
TEMPLATES = ["cover", "toc", "transition", "content", "arch",
             "flow", "compare", "case", "summary", "end",
             "statement", "overview", "kpi", "roadmap"]
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


def read_json(path, label):
    try:
        with open(path, encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"[plan_tool] {label} 无法读取：{exc}")


def visual_registries():
    page_config = read_json(PAGE_TYPES_INDEX, "页面类型索引")
    industry_config = read_json(INDUSTRIES_INDEX, "行业视觉索引")
    return page_config, industry_config


def normalize_visual_config(plan):
    page_config, industry_config = visual_registries()
    page_types = page_config.get("page_types", {})
    template_map = page_config.get("template_map", {})
    profiles = industry_config.get("profiles", {})

    industry = plan.get("industry") or "general"
    if industry not in profiles:
        sys.exit(f"[plan_tool] 未知行业视觉修饰：{industry}")
    plan["industry"] = industry

    for page in plan.get("pages", []):
        template = page.get("template", "content")
        page_type = page.get("page_type") or template_map.get(template)
        if page_type not in page_types:
            sys.exit(
                f"[plan_tool] 页面 {page.get('id', '?')} 无法解析 page_type："
                f"template={template} page_type={page_type}"
            )
        page["page_type"] = page_type
    return plan


def default_transport(provider):
    return {"agy": "native", "codex": "native", "gemini": "api"}[provider]


def resolve_image_config(provider, transport=None, model=None):
    if provider == "codex-builtin":
        provider = "codex"
        transport = transport or "native"
    if provider not in PROVIDER_TRANSPORTS:
        sys.exit(f"[plan_tool] 未知生图后端：{provider}")
    transport = transport or default_transport(provider)
    if transport not in PROVIDER_TRANSPORTS[provider]:
        allowed = ", ".join(sorted(PROVIDER_TRANSPORTS[provider]))
        sys.exit(
            f"[plan_tool] {provider} 不支持 {transport} 传输；可选：{allowed}"
        )
    if provider in ("agy", "codex") and model not in (
        None, DEFAULT_MODELS[provider]
    ):
        sys.exit(
            f"[plan_tool] {provider}/{transport} 当前模型固定为 "
            f"{DEFAULT_MODELS[provider]}"
        )
    return provider, transport, model or DEFAULT_MODELS[provider]


def normalize_image_config(plan):
    provider = plan.get("provider")
    if provider is None:
        plan.setdefault("image_transport", None)
        plan.setdefault("image_model", None)
        return plan
    legacy_transport = plan.get("image_transport")
    if provider == "codex" and not legacy_transport:
        legacy_transport = "cli"
    provider, transport, model = resolve_image_config(
        provider,
        transport=legacy_transport,
        model=plan.get("image_model"),
    )
    plan["provider"] = provider
    plan["image_transport"] = transport
    plan["image_model"] = model
    return plan


def load():
    if not os.path.exists(PLAN):
        sys.exit(f"[plan_tool] {PLAN} 不存在。请先完成 Phase 1-3 并执行 init。")
    with open(PLAN, encoding="utf-8") as f:
        plan = json.load(f)
    plan.setdefault("review", {"max_confirmations": 3, "confirmations_used": 0,
                               "checkpoints": []})
    try:
        return project_contract.normalize_plan(
            normalize_visual_config(normalize_image_config(plan))
        )
    except project_contract.ContractError as exc:
        sys.exit(f"[plan_tool] 项目契约无效：{exc}")


def save(plan):
    """Write atomically so coordinator updates cannot leave a partial state file."""
    os.makedirs(WS, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="plan.", suffix=".json", dir=WS)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PLAN)


def compatibility_rule(palette, style):
    try:
        with open(COMPATIBILITY, encoding="utf-8") as stream:
            config = json.load(stream)
        return config["combinations"][palette][style]
    except (OSError, KeyError, json.JSONDecodeError):
        sys.exit(f"[plan_tool] 未登记设计组合：{palette} × {style}。"
                 "先更新 compatibility.json 并运行 validate_design.py。")


def select_pages(plan, ids):
    wanted = {p["id"] for p in plan["pages"]} if ids == "all" else set(ids.split(","))
    found = [p for p in plan["pages"] if p["id"] in wanted]
    missing = wanted - {p["id"] for p in found}
    if missing:
        sys.exit(f"[plan_tool] 找不到页面: {sorted(missing)}")
    return found


def cmd_init(args):
    with open(args.file, encoding="utf-8") as f:
        draft = json.load(f)
    if os.path.exists(PLAN) and not args.force:
        sys.exit(f"[plan_tool] {PLAN} 已存在，如需覆盖加 --force")
    page_config, industry_config = visual_registries()
    template_map = page_config.get("template_map", {})
    page_types = page_config.get("page_types", {})
    industry = draft.get("industry") or "general"
    if industry not in industry_config.get("profiles", {}):
        sys.exit(f"[plan_tool] 未知行业视觉修饰：{industry}")

    pages = []
    for i, item in enumerate(draft.get("pages", []), 1):
        pid = item.get("id") or f"P{i:02d}"
        template = item.get("template", "content")
        if template not in TEMPLATES:
            sys.exit(f"[plan_tool] 页面 {pid} 的 template '{template}' 非法，可选: {TEMPLATES}")
        page_type = item.get("page_type") or template_map.get(template)
        if page_type not in page_types:
            sys.exit(f"[plan_tool] 页面 {pid} 的 page_type '{page_type}' 非法")
        pages.append({
            "id": pid, "template": template, "page_type": page_type,
            "title": item.get("title", ""),
            "subtitle": item.get("subtitle", ""), "points": item.get("points", []),
            "layout_hint": item.get("layout_hint", ""), "notes": item.get("notes", ""),
            "status": "pending", "prompt_file": f"prompts/{pid}.txt",
            "image": f"pages/{pid}.png",
            "requirement_refs": item.get("requirement_refs", []),
            "claim_refs": item.get("claim_refs", []),
            "source_refs": item.get("source_refs", []),
            "asset_provenance": item.get("asset_provenance", []),
            "evidence_level": item.get("evidence_level"),
            "provenance_label": item.get("provenance_label", ""),
            "reused_from": item.get("reused_from"),
            "reuse_mode": item.get("reuse_mode"),
        })
    if not pages:
        sys.exit("[plan_tool] 草稿中没有 pages")
    plan = {
        "topic": draft.get("topic", ""), "audience": draft.get("audience", ""),
        "schema_version": "2.4",
        "assurance_profile": draft.get("assurance_profile", "standard"),
        "delivery_mode": draft.get("delivery_mode", "raster_slide"),
        "requirements": draft.get("requirements", []),
        "claim_constraints": draft.get("claim_constraints", []),
        "source_registry": draft.get("source_registry", []),
        "industry": industry, "palette": None, "style": None, "provider": None,
        "image_transport": None, "image_model": None,
        "review": {"max_confirmations": 3, "confirmations_used": 0, "checkpoints": []},
        "phases": {phase: ("done" if phase in ("1_outline", "2_content", "3_pages")
                           else "pending") for phase in PHASES},
        "pages": pages,
    }
    try:
        project_contract.normalize_plan(plan)
    except project_contract.ContractError as exc:
        sys.exit(f"[plan_tool] 项目契约无效：{exc}")
    save(plan)
    for subdir in ("prompts", "pages", "pages/history", "output"):
        os.makedirs(os.path.join(WS, subdir), exist_ok=True)
    print(f"[plan_tool] 已创建 {PLAN}（{len(pages)} 页），Phase 1-3 标记为 done")


def cmd_design(args):
    plan = load()
    _page_config, industry_config = visual_registries()
    industry = getattr(args, "industry", None) or plan.get("industry") or "general"
    if industry not in industry_config.get("profiles", {}):
        sys.exit(f"[plan_tool] 未知行业视觉修饰：{industry}")
    rule = compatibility_rule(args.palette, args.style)
    if rule.get("status") == "blocked":
        alternatives = rule.get("alternatives", [])
        suffix = f"；建议：{', '.join(alternatives)}" if alternatives else ""
        sys.exit(f"[plan_tool] 非法组合：{args.palette} × {args.style}："
                 f"{rule['reason']}{suffix}")
    provider, transport, model = resolve_image_config(
        args.provider,
        transport=getattr(args, "transport", None),
        model=getattr(args, "model", None),
    )
    plan.update({
        "palette": args.palette,
        "style": args.style,
        "industry": industry,
        "provider": provider,
        "image_transport": transport,
        "image_model": model,
    })
    stale = project_contract.invalidate_stale_pages(plan)
    save(plan)
    print(
        f"[plan_tool] 设计组合已锁定: {args.palette} × {args.style} × {industry} × "
        f"{provider}/{transport}/{model}"
    )
    if stale:
        print(f"[plan_tool] 设计锁变化，已失效页面: {stale}")


def cmd_provider(args):
    plan = load()
    old = plan.get("provider")
    provider, transport, model = resolve_image_config(
        args.name,
        transport=getattr(args, "transport", None),
        model=getattr(args, "model", None),
    )
    plan.update({
        "provider": provider,
        "image_transport": transport,
        "image_model": model,
    })
    stale = project_contract.invalidate_stale_pages(plan)
    save(plan)
    print(
        f"[plan_tool] 生图后端: {old} -> {provider}/{transport}/{model}"
    )
    if stale:
        print(f"[plan_tool] 后端锁变化，已失效页面: {stale}")


def cmd_phase(args):
    plan = load()
    if args.name not in PHASES:
        sys.exit(f"[plan_tool] 未知 phase: {args.name}，可选: {PHASES}")
    if args.status == "done":
        idx = PHASES.index(args.name)
        for previous in PHASES[:idx]:
            if plan["phases"][previous] != "done":
                sys.exit(f"[plan_tool] 禁止跳步：{previous} 尚未 done，不能完成 {args.name}")
        if args.name in ("5_framework", "6_content_pages"):
            framework = {"cover", "toc", "transition", "statement", "summary", "end"}
            need_framework = args.name == "5_framework"
            required = "qa_passed" if need_framework else "approved"
            bad = [p["id"] for p in plan["pages"]
                   if ((p["template"] in framework) == need_framework)
                   and PAGE_STATUS.index(p["status"]) < PAGE_STATUS.index(required)]
            if bad:
                sys.exit(f"[plan_tool] 禁止跳步：以下页面未达 {required}: {bad}")
    plan["phases"][args.name] = args.status
    save(plan)
    print(f"[plan_tool] phase {args.name} -> {args.status}")


def cmd_page(args):
    plan = load()
    pages = select_pages(plan, args.id)
    page = pages[0]
    patch_path = getattr(args, "patch", None)
    if patch_path:
        patch = read_json(patch_path, "页面 patch")
        if not isinstance(patch, dict):
            sys.exit("[plan_tool] 页面 patch 必须是 JSON 对象")
        forbidden = {
            "id",
            "status",
            "prompt_file",
            "image",
            "prompt_input_hash",
            "image_input_hash",
            "dirty_reasons",
        }
        illegal = forbidden.intersection(patch)
        if illegal:
            sys.exit(f"[plan_tool] 页面 patch 禁止修改：{sorted(illegal)}")
        page.update(patch)
        try:
            project_contract.validate_plan(plan)
        except project_contract.ContractError as exc:
            sys.exit(f"[plan_tool] 项目契约无效：{exc}")
        project_contract.invalidate_stale_pages(plan)
    if args.status:
        page["status"] = args.status
        if args.status == "prompted":
            project_contract.record_prompt_hash(plan, page)
        elif PAGE_STATUS.index(args.status) >= PAGE_STATUS.index("generated"):
            project_contract.record_image_hash(plan, page)
    if args.image:
        page["image"] = args.image
    if args.notes is not None:
        page["notes"] = args.notes
    save(plan)
    print(f"[plan_tool] page {args.id}: status={page['status']}")


def cmd_pages(args):
    plan = load()
    pages = select_pages(plan, args.ids)
    for page in pages:
        page["status"] = args.status
        if args.status == "prompted":
            project_contract.record_prompt_hash(plan, page)
        elif PAGE_STATUS.index(args.status) >= PAGE_STATUS.index("generated"):
            project_contract.record_image_hash(plan, page)
    save(plan)
    print(f"[plan_tool] {len(pages)} pages -> {args.status}: {[p['id'] for p in pages]}")


def cmd_review(args):
    plan = load()
    review = plan["review"]
    if review["confirmations_used"] >= review["max_confirmations"]:
        sys.exit("[plan_tool] 图片确认次数已达到上限 3；必须合并处理剩余意见。")
    pages = select_pages(plan, args.ids)
    if args.result == "approved":
        bad = [p["id"] for p in pages
               if PAGE_STATUS.index(p["status"]) < PAGE_STATUS.index("qa_passed")]
        if bad:
            sys.exit(f"[plan_tool] 以下页面尚未 qa_passed，不能确认通过: {bad}")
    review["confirmations_used"] += 1
    checkpoint = {"number": review["confirmations_used"], "type": args.type,
                  "pages": [p["id"] for p in pages], "result": args.result}
    review["checkpoints"].append(checkpoint)
    if args.result == "approved":
        for page in pages:
            page["status"] = "approved"
    else:
        requested = {page["id"] for page in pages}
        # A full-deck review approves every QA-passed page the user did not request
        # changes for. Only named revision pages return to pending.
        if args.type == "full-deck":
            for page in plan["pages"]:
                if page["id"] not in requested and PAGE_STATUS.index(page["status"]) >= \
                        PAGE_STATUS.index("qa_passed"):
                    page["status"] = "approved"
        for page in pages:
            page["status"] = "pending"
    save(plan)
    remaining = review["max_confirmations"] - review["confirmations_used"]
    print(f"[plan_tool] review #{checkpoint['number']} {args.type}: {args.result} "
          f"({len(pages)} pages)，剩余 {remaining} 次")


def cmd_status(_args):
    plan = load()
    print(f"主题: {plan['topic']}  设计: {plan.get('palette')} × {plan.get('style')}"
          f" × {plan.get('industry')}"
          f" × {plan.get('provider')}/{plan.get('image_transport')}"
          f"/{plan.get('image_model')}")
    for phase in PHASES:
        print(f"  {phase:18s} {plan['phases'][phase]}")
    counts = {}
    for page in plan["pages"]:
        counts[page["status"]] = counts.get(page["status"], 0) + 1
    print(f"页面({len(plan['pages'])}): " + " ".join(f"{k}={v}" for k, v in counts.items()))
    review = plan["review"]
    print(f"图片确认: {review['confirmations_used']}/{review['max_confirmations']}")
    nxt = next((phase for phase in PHASES if plan["phases"][phase] != "done"), None)
    print(f"下一步: {nxt or '全部完成 ✓'}")


def cmd_check(args):
    plan = load()
    level = PAGE_STATUS.index(args.min_status)
    bad = [f"{p['id']}({p['status']})" for p in plan["pages"]
           if PAGE_STATUS.index(p["status"]) < level]
    if bad:
        print(f"[plan_tool] GATE FAILED，以下页面未达 {args.min_status}: {', '.join(bad)}")
        sys.exit(1)
    print(f"[plan_tool] GATE PASSED（全部页面 >= {args.min_status}）")


def cmd_lint(args):
    plan = load()
    ids = None if args.ids == "all" else set(args.ids.split(","))
    findings = project_contract.lint_pages(plan, page_ids=ids)
    if findings:
        print(project_contract.format_findings(findings))
    errors = [item for item in findings if item["severity"] == "error"]
    if errors:
        sys.exit(
            f"[plan_tool] LINT FAILED（{len(errors)} 个错误）\n"
            + project_contract.format_findings(errors)
        )
    warnings = [item for item in findings if item["severity"] == "warning"]
    print(
        f"[plan_tool] LINT PASSED（{len(warnings)} 个警告）"
    )


def cmd_contract(args):
    plan = load()
    update = read_json(args.file, "项目契约")
    if not isinstance(update, dict):
        sys.exit("[plan_tool] 项目契约文件必须是 JSON 对象")
    allowed = {
        "assurance_profile",
        "delivery_mode",
        "requirements",
        "claim_constraints",
        "source_registry",
    }
    unknown = set(update) - allowed
    if unknown:
        sys.exit(f"[plan_tool] 项目契约包含未知顶层字段：{sorted(unknown)}")
    plan.update(update)
    try:
        project_contract.validate_plan(plan)
    except project_contract.ContractError as exc:
        sys.exit(f"[plan_tool] 项目契约无效：{exc}")
    stale = project_contract.invalidate_stale_pages(plan)
    save(plan)
    print(f"[plan_tool] 项目契约已更新；失效页面: {stale or '无'}")


def cmd_sync(_args):
    plan = load()
    stale = project_contract.invalidate_stale_pages(plan)
    save(plan)
    print(f"[plan_tool] 同步完成；失效页面: {stale or '无'}")


def cmd_sync_check(_args):
    plan = load()
    findings = project_contract.sync_findings(plan)
    if findings:
        details = ", ".join(
            f"{item['page']}({item['reason']})" for item in findings
        )
        sys.exit(f"[plan_tool] STALE：{details}")
    print("[plan_tool] SYNC PASSED（全部页面与项目输入一致）")


def cmd_reuse(args):
    plan = load()
    page = select_pages(plan, args.id)[0]
    if args.source == page["id"]:
        sys.exit(f"[plan_tool] 页面 {page['id']} 不得复用自身")
    page["reused_from"] = args.source
    page["reuse_mode"] = "exact_asset"
    try:
        project_contract.validate_plan(plan)
    except project_contract.ContractError as exc:
        sys.exit(f"[plan_tool] 页面复用无效：{exc}")
    stale = project_contract.invalidate_stale_pages(plan)
    save(plan)
    print(
        f"[plan_tool] {page['id']} exact_asset -> {args.source}；"
        f"失效页面: {stale or '无'}"
    )


def cmd_export_outline(args):
    plan = load()
    target = project_contract.export_outline(plan, args.out)
    print(f"[plan_tool] 已导出最终大纲：{target}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    parser = sub.add_parser("init"); parser.add_argument("--file", required=True)
    parser.add_argument("--force", action="store_true"); parser.set_defaults(fn=cmd_init)
    parser = sub.add_parser("design")
    parser.add_argument("--palette", required=True); parser.add_argument("--style", required=True)
    parser.add_argument("--industry")
    parser.add_argument("--provider", required=True,
                        choices=["agy", "gemini", "codex", "codex-builtin"])
    parser.add_argument("--transport", choices=["native", "cli", "api"])
    parser.add_argument("--model")
    parser.set_defaults(fn=cmd_design)
    parser = sub.add_parser("provider"); parser.add_argument("--name", required=True,
        choices=["agy", "codex", "gemini", "codex-builtin"])
    parser.add_argument("--transport", choices=["native", "cli", "api"])
    parser.add_argument("--model"); parser.set_defaults(fn=cmd_provider)
    parser = sub.add_parser("phase"); parser.add_argument("--name", required=True)
    parser.add_argument("--status", required=True, choices=["pending", "done"])
    parser.set_defaults(fn=cmd_phase)
    parser = sub.add_parser("page"); parser.add_argument("--id", required=True)
    parser.add_argument("--status", choices=PAGE_STATUS); parser.add_argument("--image")
    parser.add_argument("--notes"); parser.add_argument("--patch")
    parser.set_defaults(fn=cmd_page)
    parser = sub.add_parser("pages"); parser.add_argument("--ids", required=True)
    parser.add_argument("--status", required=True, choices=PAGE_STATUS); parser.set_defaults(fn=cmd_pages)
    parser = sub.add_parser("review"); parser.add_argument("--type", required=True,
        choices=["design-sample", "full-deck", "revision"])
    parser.add_argument("--ids", required=True); parser.add_argument("--result", required=True,
        choices=["approved", "changes-requested"]); parser.set_defaults(fn=cmd_review)
    parser = sub.add_parser("status"); parser.set_defaults(fn=cmd_status)
    parser = sub.add_parser("check"); parser.add_argument("--min-status", default="approved",
        choices=PAGE_STATUS); parser.set_defaults(fn=cmd_check)
    parser = sub.add_parser("lint"); parser.add_argument("--ids", default="all")
    parser.set_defaults(fn=cmd_lint)
    parser = sub.add_parser("contract"); parser.add_argument("--file", required=True)
    parser.set_defaults(fn=cmd_contract)
    parser = sub.add_parser("sync"); parser.set_defaults(fn=cmd_sync)
    parser = sub.add_parser("sync-check"); parser.set_defaults(fn=cmd_sync_check)
    parser = sub.add_parser("reuse"); parser.add_argument("--id", required=True)
    parser.add_argument("--from", required=True, dest="source")
    parser.set_defaults(fn=cmd_reuse)
    parser = sub.add_parser("export-outline")
    parser.add_argument("--out", default=os.path.join(WS, "final_outline.md"))
    parser.set_defaults(fn=cmd_export_outline)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
