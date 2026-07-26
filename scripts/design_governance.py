#!/usr/bin/env python3
"""Shared visual-governance checks for plans and prompt generation."""
import json
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO / "references" / "design"

LAYOUT_PATTERNS = (
    (
        "cards",
        re.compile(
            r"三(?:栏|列|等分).{0,8}卡|卡片墙|"
            r"three\s+(?:equal\s+)?cards?|card\s+(?:wall|grid)",
            re.I,
        ),
    ),
    (
        "split",
        re.compile(
            r"左图右文|右图左文|左右对分|左右分栏|"
            r"\bsplit\b|image\s*(?:and|with|\+)\s*text",
            re.I,
        ),
    ),
    (
        "evidence",
        re.compile(
            r"主图.{0,8}注释|证据|截图|现场(?:图|照片)|"
            r"\bevidence\b|\bscreenshot\b|\bphoto\b",
            re.I,
        ),
    ),
    (
        "layered",
        re.compile(r"分层|架构|layered|architecture", re.I),
    ),
    (
        "flow",
        re.compile(r"流程|路径|时间轴|阶段轴|journey|timeline|roadmap", re.I),
    ),
    (
        "matrix",
        re.compile(r"矩阵|matrix|网格总览|overview\s+grid", re.I),
    ),
)


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def load_design(design=DEFAULT_DESIGN):
    design = Path(design)
    return (
        read_json(design / "governance.json"),
        read_json(design / "compatibility.json"),
    )


def finding(severity, code, message, pages=None):
    item = {"severity": severity, "code": code, "message": message}
    if pages:
        item["pages"] = list(pages)
    return item


def layout_family(page):
    explicit = str(page.get("layout_family") or "").strip().lower()
    if explicit:
        return explicit
    hint = str(page.get("layout_hint") or "").strip()
    if not hint:
        return None
    for family, pattern in LAYOUT_PATTERNS:
        if pattern.search(hint):
            return family
    return None


def _combination_findings(plan, governance, compatibility):
    palette = plan.get("palette")
    style = plan.get("style")
    if not palette or not style:
        return [
            finding(
                "error",
                "design-not-locked",
                "plan.json 尚未锁定 palette 和 style",
            )
        ]
    try:
        rule = compatibility["combinations"][palette][style]
    except KeyError:
        return [
            finding(
                "error",
                "unregistered-combination",
                f"未登记设计组合：{palette} × {style}",
            )
        ]

    results = []
    status = rule.get("status")
    if status == "blocked":
        results.append(
            finding(
                "error",
                "blocked-combination",
                f"{palette} × {style} 被禁止：{rule.get('reason', '材质不兼容')}",
            )
        )
        return results
    if status in {"specialized", "legacy"}:
        alternatives = rule.get("alternatives", [])
        alternative_text = (
            f"；替代：{', '.join(alternatives)}" if alternatives else ""
        )
        results.append(
            finding(
                "warning",
                f"{status}-combination",
                f"{palette} × {style} 为 {status} 组合："
                f"{rule.get('reason', '')}{alternative_text}",
            )
        )

    palette_tier = governance["palette_profiles"].get(palette, {}).get("tier")
    style_tier = governance["style_profiles"].get(style, {}).get("tier")
    if palette_tier in {"legacy", "specialized"}:
        results.append(
            finding(
                "warning",
                f"{palette_tier}-palette",
                f"配色 {palette} 属于 {palette_tier} 层级，不作为通用新项目默认",
            )
        )
    if style_tier == "specialized":
        results.append(
            finding(
                "warning",
                "specialized-style",
                f"风格 {style} 属于 specialized 层级，需有明确材质意图",
            )
        )
    return results


def _rhythm_findings(plan, deck_rules):
    pages = plan.get("pages", [])
    maximum = int(deck_rules.get("max_consecutive_layout_family", 2))
    results = []
    run_family = None
    run_pages = []
    reported = set()

    def flush_run():
        if run_family and len(run_pages) > maximum:
            key = (run_family, tuple(run_pages))
            if key not in reported:
                results.append(
                    finding(
                        "warning",
                        "repeated-layout-family",
                        f"布局族 {run_family} 连续出现 {len(run_pages)} 页，"
                        f"超过上限 {maximum}",
                        run_pages,
                    )
                )
                reported.add(key)

    card_pages = []
    for page in pages:
        family = layout_family(page)
        if family == "cards":
            card_pages.append(page.get("id", "?"))
        if family and family == run_family:
            run_pages.append(page.get("id", "?"))
            continue
        flush_run()
        run_family = family
        run_pages = [page.get("id", "?")] if family else []
    flush_run()

    card_max = int(deck_rules.get("max_repeated_generic_card_pages", 1))
    if len(card_pages) > card_max:
        results.append(
            finding(
                "warning",
                "generic-card-repetition",
                f"三等分卡片/卡片墙提示出现 {len(card_pages)} 页，超过上限 {card_max}",
                card_pages,
            )
        )
    return results


def lint_plan(plan, design=DEFAULT_DESIGN):
    governance, compatibility = load_design(design)
    return (
        _combination_findings(plan, governance, compatibility)
        + _rhythm_findings(plan, governance.get("deck_rules", {}))
    )


def format_findings(findings):
    lines = []
    for item in findings:
        pages = f" [{', '.join(item.get('pages', []))}]" if item.get("pages") else ""
        lines.append(
            f"{item['severity'].upper()} {item['code']}{pages}: {item['message']}"
        )
    return "\n".join(lines)
