#!/usr/bin/env python3
"""Validate layered visual definitions and every explicit palette × style decision."""
import argparse
import json
import os
from pathlib import Path
import re
import sys

import generate_style_refs

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO / "references" / "design"
REQUIRED_LEGACY_TOKENS = {
    "PRIMARY", "SECONDARY", "ACCENT", "BG", "TITLE", "BODY", "OK", "WARN"
}
REQUIRED_SEMANTIC_TOKENS = {
    "BACKGROUND", "SURFACE", "STRUCTURE", "FOCUS",
    "FOCUS_TEXT",
    "TEXT_PRIMARY", "TEXT_SECONDARY", "BORDER",
    "INVERSE_BACKGROUND", "INVERSE_TEXT",
    "STATUS_OK", "STATUS_OK_TEXT",
    "STATUS_WARN", "STATUS_WARN_TEXT",
    "STATUS_RISK", "STATUS_RISK_TEXT",
}
TEXT_ON_LIGHT_ROLES = {
    "TEXT_PRIMARY", "TEXT_SECONDARY", "FOCUS_TEXT",
    "STATUS_OK_TEXT", "STATUS_WARN_TEXT", "STATUS_RISK_TEXT",
}
VALID_STATUSES = {"recommended", "allowed", "specialized", "legacy", "blocked"}
VALID_PALETTE_TIERS = {"core", "brand", "conditional", "specialized", "legacy"}
VALID_STYLE_TIERS = {"core", "conditional", "specialized"}
REQUIRED_STYLE_PROFILE_FIELDS = {
    "tier", "density", "variance", "shape", "radius", "shadow", "material",
    "image", "annotation", "micro_label_budget", "reference_mode",
    "reference_roles", "typography",
}
REQUIRED_TYPOGRAPHY_FIELDS = {
    "family_budget", "family_policy", "hierarchy_levels",
    "display", "body", "small_text",
}
REQUIRED_SPATIAL_FIELDS = {
    "title_axis", "semantic_anchor", "transition_anchor",
}
REQUIRED_GLASS_LAYER_FIELDS = {
    "max_translucent_layers", "glass_on_glass",
    "solid_text_backing", "dense_page_policy",
}


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


def token_hexes(text):
    """Parse token-table hex colors without depending on Markdown heading wording."""
    values = {}
    for line in text.splitlines():
        match = re.match(r"\|\s*`\{(\w+)\}`\s*\|\s*`([^`]+)`", line)
        if not match:
            continue
        values[match.group(1)] = re.findall(r"#[0-9A-Fa-f]{6}", match.group(2))
    return values


def relative_luminance(hex_color):
    channels = [
        int(hex_color[index:index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        value / 12.92 if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def validate_contrast(palette, values, minimum, errors):
    backgrounds = values.get("BACKGROUND", []) + values.get("SURFACE", [])
    for role in sorted(TEXT_ON_LIGHT_ROLES):
        colors = values.get(role, [])
        for color in colors:
            for background in backgrounds:
                ratio = contrast_ratio(color, background)
                if ratio + 1e-9 < minimum:
                    errors.append(
                        f"{palette}: {role} {color} 与背景 {background} "
                        f"对比度 {ratio:.2f}:1，低于 {minimum:.1f}:1"
                    )
    for text_color in values.get("INVERSE_TEXT", []):
        for background in values.get("INVERSE_BACKGROUND", []):
            ratio = contrast_ratio(text_color, background)
            if ratio + 1e-9 < minimum:
                errors.append(
                    f"{palette}: INVERSE_TEXT {text_color} 与反相背景 {background} "
                    f"对比度 {ratio:.2f}:1，低于 {minimum:.1f}:1"
                )


def validate_governance(design, palettes, styles, errors):
    governance = load_json(design / "governance.json", "governance.json", errors)
    if governance is None:
        return {}
    if governance.get("version", 0) < 2:
        errors.append("governance.json: v2.6 视觉治理要求 version >= 2")
    deck_rules = governance.get("deck_rules")
    if not isinstance(deck_rules, dict):
        errors.append("governance.json: deck_rules 必须是对象")
        deck_rules = {}
    minimum = deck_rules.get("minimum_text_contrast")
    if (
        isinstance(minimum, bool)
        or not isinstance(minimum, (int, float))
        or minimum < 4.5
    ):
        errors.append("governance.json: minimum_text_contrast 必须 >= 4.5")
    integer_rules = {
        "max_consecutive_layout_family": 1,
        "max_repeated_generic_card_pages": 0,
        "max_focus_objects_per_page": 1,
        "max_micro_labels_per_page": 1,
    }
    for field, lower_bound in integer_rules.items():
        value = deck_rules.get(field)
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < lower_bound
        ):
            errors.append(
                f"governance.json: {field} 必须是 >= {lower_bound} 的整数"
            )
    spatial = deck_rules.get("spatial_consistency")
    if not isinstance(spatial, dict):
        errors.append("governance.json: spatial_consistency 必须是对象")
    else:
        missing = REQUIRED_SPATIAL_FIELDS - set(spatial)
        if missing:
            errors.append(
                "governance.json: spatial_consistency "
                f"缺少字段 {sorted(missing)}"
            )
        for field in REQUIRED_SPATIAL_FIELDS:
            value = spatial.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"governance.json: spatial_consistency.{field} "
                    "必须是非空字符串"
                )
    if deck_rules.get("reference_width") != generate_style_refs.WIDTH:
        errors.append(
            f"governance.json: reference_width 必须是 "
            f"{generate_style_refs.WIDTH}"
        )
    if deck_rules.get("reference_height") != generate_style_refs.HEIGHT:
        errors.append(
            f"governance.json: reference_height 必须是 "
            f"{generate_style_refs.HEIGHT}"
        )
    global_micro_label_budget = deck_rules.get(
        "max_micro_labels_per_page",
        max(
            (
                profile.get("micro_label_budget", 0)
                for profile in governance.get("style_profiles", {}).values()
                if isinstance(profile, dict)
            ),
            default=0,
        ),
    )

    palette_profiles = governance.get("palette_profiles", {})
    style_profiles = governance.get("style_profiles", {})
    if set(palette_profiles) != set(palettes):
        errors.append(
            "governance.json: palette_profiles 与 palette 文件不一致"
        )
    if set(style_profiles) != set(styles):
        errors.append(
            "governance.json: style_profiles 与 style 文件不一致"
        )
    for palette, profile in palette_profiles.items():
        tier = profile.get("tier") if isinstance(profile, dict) else None
        if tier not in VALID_PALETTE_TIERS:
            errors.append(f"governance.json: {palette} palette tier 非法: {tier}")
    for style, profile in style_profiles.items():
        if not isinstance(profile, dict):
            errors.append(f"governance.json: {style} style profile 必须是对象")
            continue
        missing = REQUIRED_STYLE_PROFILE_FIELDS - set(profile)
        if missing:
            errors.append(
                f"governance.json: {style} 缺少字段 {sorted(missing)}"
            )
        if profile.get("tier") not in VALID_STYLE_TIERS:
            errors.append(
                f"governance.json: {style} style tier 非法: {profile.get('tier')}"
            )
        micro_label_budget = profile.get("micro_label_budget")
        if (
            isinstance(micro_label_budget, bool)
            or not isinstance(micro_label_budget, int)
            or micro_label_budget < 1
        ):
            errors.append(
                f"governance.json: {style} micro_label_budget 必须是正整数"
            )
        elif (
            isinstance(global_micro_label_budget, int)
            and micro_label_budget > global_micro_label_budget
        ):
            errors.append(
                f"governance.json: {style} micro_label_budget "
                f"{micro_label_budget} 超过 max_micro_labels_per_page "
                f"{global_micro_label_budget}"
            )
        for field in ("density", "variance"):
            bounds = profile.get(field)
            if (
                not isinstance(bounds, list)
                or len(bounds) != 2
                or not all(isinstance(value, int) for value in bounds)
                or not 1 <= bounds[0] <= bounds[1] <= 10
            ):
                errors.append(
                    f"governance.json: {style} {field} 必须是 1-10 的双值范围"
                )
        typography = profile.get("typography")
        if not isinstance(typography, dict):
            errors.append(
                f"governance.json: {style} typography 必须是对象"
            )
        else:
            missing_typography = REQUIRED_TYPOGRAPHY_FIELDS - set(typography)
            if missing_typography:
                errors.append(
                    f"governance.json: {style} typography "
                    f"缺少字段 {sorted(missing_typography)}"
                )
            family_budget = typography.get("family_budget")
            if (
                isinstance(family_budget, bool)
                or not isinstance(family_budget, int)
                or family_budget not in {1, 2}
            ):
                errors.append(
                    f"governance.json: {style} typography.family_budget "
                    "必须是 1 或 2"
                )
            hierarchy_levels = typography.get("hierarchy_levels")
            if (
                isinstance(hierarchy_levels, bool)
                or not isinstance(hierarchy_levels, int)
                or not 3 <= hierarchy_levels <= 5
            ):
                errors.append(
                    f"governance.json: {style} typography.hierarchy_levels "
                    "必须是 3-5 的整数"
                )
            for field in (
                "family_policy", "display", "body", "small_text"
            ):
                value = typography.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"governance.json: {style} typography.{field} "
                        "必须是非空字符串"
                    )
        mode = profile.get("reference_mode")
        roles = profile.get("reference_roles")
        if mode not in {"generated", "text-only"}:
            errors.append(
                f"governance.json: {style} reference_mode 非法: {mode}"
            )
        if mode == "generated" and (
            not isinstance(roles, list) or len(roles) != 3
        ):
            errors.append(
                f"governance.json: {style} generated 风格必须登记 3 个参考角色"
            )
        if mode == "text-only" and roles != []:
            errors.append(
                f"governance.json: {style} text-only 风格的 reference_roles 必须为空"
            )
    glass_profile = style_profiles.get("glass-3d", {})
    glass_layers = (
        glass_profile.get("material_layers")
        if isinstance(glass_profile, dict)
        else None
    )
    if not isinstance(glass_layers, dict):
        errors.append("governance.json: glass-3d material_layers 必须是对象")
    else:
        missing_glass = REQUIRED_GLASS_LAYER_FIELDS - set(glass_layers)
        if missing_glass:
            errors.append(
                "governance.json: glass-3d material_layers "
                f"缺少字段 {sorted(missing_glass)}"
            )
        if glass_layers.get("max_translucent_layers") != 2:
            errors.append(
                "governance.json: glass-3d max_translucent_layers 必须为 2"
            )
        if glass_layers.get("glass_on_glass") is not False:
            errors.append(
                "governance.json: glass-3d glass_on_glass 必须为 false"
            )
        if glass_layers.get("solid_text_backing") is not True:
            errors.append(
                "governance.json: glass-3d solid_text_backing 必须为 true"
            )
        dense_page_policy = glass_layers.get("dense_page_policy")
        if (
            not isinstance(dense_page_policy, str)
            or not dense_page_policy.strip()
        ):
            errors.append(
                "governance.json: glass-3d dense_page_policy 必须是非空字符串"
            )
    return governance


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

    if config.get("version", 0) < 4:
        errors.append("compatibility.json: v2.6 视觉系统要求 version >= 4")
    if sorted(config.get("palettes", [])) != palettes:
        errors.append(f"配置 palettes 与文件不一致: config={config.get('palettes')} files={palettes}")
    if sorted(config.get("styles", [])) != styles:
        errors.append(f"配置 styles 与文件不一致: config={config.get('styles')} files={styles}")

    governance = validate_governance(design, palettes, styles, errors)
    minimum_contrast = governance.get("deck_rules", {}).get(
        "minimum_text_contrast", 4.5
    )
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
        values = token_hexes(text)
        if not missing_semantic:
            validate_contrast(
                palette, values, float(minimum_contrast), errors
            )

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
            if status in {"specialized", "legacy"} and not rule.get("reason"):
                errors.append(f"{palette} × {style}: {status} 必须提供 reason")
            if status == "legacy" and not rule.get("alternatives"):
                errors.append(f"{palette} × {style}: legacy 必须提供 alternatives")
            for alternative in rule.get("alternatives", []):
                if (
                    not isinstance(alternative, str)
                    or alternative.count(" × ") != 1
                ):
                    errors.append(
                        f"{palette} × {style}: 替代组合格式无效: {alternative!r}"
                    )
                    continue
                alternative_palette, alternative_style = alternative.split(
                    " × ", 1
                )
                target = combinations.get(alternative_palette, {}).get(
                    alternative_style
                )
                if not isinstance(target, dict):
                    errors.append(
                        f"{palette} × {style}: 替代组合未登记: {alternative}"
                    )
                elif target.get("status") in {"blocked", "legacy"}:
                    errors.append(
                        f"{palette} × {style}: 替代组合不可作为现代替代: "
                        f"{alternative} ({target.get('status')})"
                    )
        recommended = [
            style
            for style, rule in row.items()
            if isinstance(rule, dict) and rule.get("status") == "recommended"
        ]
        if len(recommended) > 3:
            errors.append(
                f"{palette}: recommended 风格超过 3 个: {recommended}"
            )
        palette_tier = governance.get("palette_profiles", {}).get(
            palette, {}
        ).get("tier")
        if palette_tier == "legacy" and recommended:
            errors.append(
                f"{palette}: legacy 配色不得含 recommended 组合: {recommended}"
            )

    for style in styles:
        path = design / "styles" / f"{style}.md"
        text = path.read_text(encoding="utf-8")
        if not re.search(r"##\s*风格提示词骨架.*?```\n.+?```", text, re.S):
            errors.append(f"{style}: 缺少风格提示词骨架代码块")

    errors.extend(generate_style_refs.validate_assets(design))

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
