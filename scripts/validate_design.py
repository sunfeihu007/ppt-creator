#!/usr/bin/env python3
"""Validate design definitions and require an explicit decision for every combination."""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DESIGN = os.path.join(REPO, "references", "design")
REQUIRED_TOKENS = {"PRIMARY", "SECONDARY", "ACCENT", "BG", "TITLE", "BODY", "OK", "WARN"}
VALID_STATUSES = {"recommended", "allowed", "blocked"}


def ids_in(path):
    return sorted(os.path.splitext(name)[0] for name in os.listdir(path) if name.endswith(".md"))


def validate(design):
    errors = []
    palettes = ids_in(os.path.join(design, "palettes"))
    styles = ids_in(os.path.join(design, "styles"))
    config_path = os.path.join(design, "compatibility.json")
    try:
        config = json.load(open(config_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"compatibility.json 无法读取: {exc}"]

    if sorted(config.get("palettes", [])) != palettes:
        errors.append(f"配置 palettes 与文件不一致: config={config.get('palettes')} files={palettes}")
    if sorted(config.get("styles", [])) != styles:
        errors.append(f"配置 styles 与文件不一致: config={config.get('styles')} files={styles}")

    for palette in palettes:
        path = os.path.join(design, "palettes", palette + ".md")
        text = open(path, encoding="utf-8").read()
        tokens = set(re.findall(r"`\{(\w+)\}`", text))
        missing = REQUIRED_TOKENS - tokens
        if missing:
            errors.append(f"{palette}: 缺少 Token {sorted(missing)}")
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

    for style in styles:
        text = open(os.path.join(design, "styles", style + ".md"), encoding="utf-8").read()
        if "```" not in text or "## 页面类型模板" not in text:
            errors.append(f"{style}: 缺少页面模板代码块")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", default=DEFAULT_DESIGN)
    args = ap.parse_args()
    errors = validate(args.design)
    if errors:
        print("[validate_design] FAILED")
        for error in errors:
            print(" - " + error)
        sys.exit(1)
    config = json.load(open(os.path.join(args.design, "compatibility.json"), encoding="utf-8"))
    count = len(config["palettes"]) * len(config["styles"])
    print(f"[validate_design] PASSED: {len(config['palettes'])} palettes × "
          f"{len(config['styles'])} styles = {count} combinations")


if __name__ == "__main__":
    main()
