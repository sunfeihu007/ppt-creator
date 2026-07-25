#!/usr/bin/env python3
"""Validate layered visual definitions and every explicit palette × style decision."""
import argparse
import json
import os
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO / "references" / "design"
REQUIRED_LEGACY_TOKENS = {
    "PRIMARY", "SECONDARY", "ACCENT", "BG", "TITLE", "BODY", "OK", "WARN"
}
REQUIRED_SEMANTIC_TOKENS = {
    "BACKGROUND", "SURFACE", "STRUCTURE", "FOCUS",
    "TEXT_PRIMARY", "TEXT_SECONDARY", "BORDER",
    "INVERSE_BACKGROUND", "INVERSE_TEXT",
    "STATUS_OK", "STATUS_WARN", "STATUS_RISK",
}
VALID_STATUSES = {"recommended", "allowed", "blocked"}


def ids_in(path):
    return sorted(item.stem for item in Path(path).iterdir() if item.suffix == ".md")


def load_json(path, label, errors):
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label} 无法读取: {exc}")
        return None


def has_prompt_fragment(text):
    return bool(re.search(r"##\s*提示词片段.*?```\n.+?```", text, re.S))


def validate_registry(design, directory, index, collection_key, errors):
    registry_dir = design / directory
    config = load_json(registry_dir / index, f"{directory}/{index}", errors)
    if config is None:
        return {}
    entries = config.get(collection_key)
    if not isinstance(entries, dict) or not entries:
        errors.append(f"{directory}/{index}: {collection_key} 必须是非空对象")
        return {}
    for item_id, entry in entries.items():
        filename = entry.get("file") if isinstance(entry, dict) else None
        if not filename:
            errors.append(f"{directory}/{item_id}: 缺少 file")
            continue
        relative = f"{directory}/{filename}"
        path = registry_dir / filename
        if not path.is_file():
            errors.append(f"{relative}: 索引指向的文件不存在")
            continue
        text = path.read_text(encoding="utf-8")
        if not has_prompt_fragment(text):
            errors.append(f"{relative}: 缺少提示词片段代码块")
    return entries


def validate(design):
    design = Path(design)
    errors = []
    palettes = ids_in(design / "palettes")
    styles = ids_in(design / "styles")
    config = load_json(design / "compatibility.json", "compatibility.json", errors)
    if config is None:
        return errors

    if config.get("version", 0) < 2:
        errors.append("compatibility.json: v2.3 视觉系统要求 version >= 2")
    if sorted(config.get("palettes", [])) != palettes:
        errors.append(f"配置 palettes 与文件不一致: config={config.get('palettes')} files={palettes}")
    if sorted(config.get("styles", [])) != styles:
        errors.append(f"配置 styles 与文件不一致: config={config.get('styles')} files={styles}")

    for palette in palettes:
        path = design / "palettes" / f"{palette}.md"
        text = path.read_text(encoding="utf-8")
        tokens = set(re.findall(r"`\{(\w+)\}`", text))
        missing_legacy = REQUIRED_LEGACY_TOKENS - tokens
        if missing_legacy:
            errors.append(f"{palette}: 缺少兼容 Token {sorted(missing_legacy)}")
        missing_semantic = REQUIRED_SEMANTIC_TOKENS - tokens
        if missing_semantic:
            errors.append(f"{palette}: 缺少语义 Token {sorted(missing_semantic)}")
        if not re.search(r"##\s*提示词配色描述段.*?```\n.+?```", text, re.S):
            errors.append(f"{palette}: 缺少提示词配色描述段")

    combinations = config.get("combinations", {})
    for palette in palettes:
        row = combinations.get(palette, {})
        extra = set(row) - set(styles)
        if extra:
            errors.append(f"{palette}: 包含未知风格 {sorted(extra)}")
        for style in styles:
            rule = row.get(style)
            if not isinstance(rule, dict):
                errors.append(f"{palette} × {style}: 未登记兼容性")
                continue
            status = rule.get("status")
            if status not in VALID_STATUSES:
                errors.append(f"{palette} × {style}: 非法 status={status}")
            if status == "blocked" and not rule.get("reason"):
                errors.append(f"{palette} × {style}: blocked 必须提供 reason")
            if status == "blocked" and not rule.get("alternatives"):
                errors.append(f"{palette} × {style}: blocked 必须提供 alternatives")

    for style in styles:
        path = design / "styles" / f"{style}.md"
        text = path.read_text(encoding="utf-8")
        if not re.search(r"##\s*风格提示词骨架.*?```\n.+?```", text, re.S):
            errors.append(f"{style}: 缺少风格提示词骨架代码块")

    page_types = validate_registry(
        design, "page-types", "index.json", "page_types", errors
    )
    page_config = load_json(
        design / "page-types" / "index.json", "page-types/index.json", errors
    )
    if page_config:
        for template, page_type in page_config.get("template_map", {}).items():
            if page_type not in page_types:
                errors.append(
                    f"page-types/index.json: template {template} 指向未知页面类型 {page_type}"
                )

    industries = validate_registry(
        design, "industries", "index.json", "profiles", errors
    )
    for industry, entry in industries.items():
        palette = entry.get("recommended_palette")
        style = entry.get("recommended_style")
        if palette not in palettes:
            errors.append(f"industries/{industry}: 推荐未知配色 {palette}")
            continue
        if style not in styles:
            errors.append(f"industries/{industry}: 推荐未知风格 {style}")
            continue
        rule = combinations.get(palette, {}).get(style, {})
        if rule.get("status") == "blocked":
            errors.append(
                f"industries/{industry}: 默认组合 {palette} × {style} 被标记为 blocked"
            )
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", default=str(DEFAULT_DESIGN))
    args = ap.parse_args()
    errors = validate(args.design)
    if errors:
        print("[validate_design] FAILED")
        for error in errors:
            print(" - " + error)
        sys.exit(1)

    design = Path(args.design)
    with (design / "compatibility.json").open(encoding="utf-8") as stream:
        config = json.load(stream)
    with (design / "page-types" / "index.json").open(encoding="utf-8") as stream:
        page_config = json.load(stream)
    with (design / "industries" / "index.json").open(encoding="utf-8") as stream:
        industry_config = json.load(stream)
    count = len(config["palettes"]) * len(config["styles"])
    print(
        f"[validate_design] PASSED: {len(config['palettes'])} palettes × "
        f"{len(config['styles'])} styles = {count} combinations; "
        f"{len(page_config['page_types'])} page types; "
        f"{len(industry_config['profiles'])} industries"
    )


if __name__ == "__main__":
    main()
