#!/usr/bin/env python3
"""提示词拼装器：风格家族 + 页面类型 + 行业修饰 + 配色 + 内容 + 全局约束。

AI 只负责在 plan.json 里填好每页的 title/points/layout_hint，
提示词的固定部分（风格、页面类型、行业视觉、配色、禁止项）由本脚本拼装，
从机制上杜绝"风格漂移"和"漏写约束"。

用法:
  make_prompt.py --page P01 [--design references/design] [--print]
输出: $PPTC_WORKSPACE/prompts/P01.txt（同时列出应垫图的参考图路径）
"""
import argparse
import json
import os
import re
import sys

import design_governance
import project_contract

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# v2.2 及第三方旧风格的兼容回退：template -> 风格文件旧模板关键词。
TEMPLATE_KEYWORDS = {
    "cover": ["封面"], "toc": ["目录"], "transition": ["封面"],
    "arch": ["架构"], "flow": ["流程"], "compare": ["对比", "流程"],
    "case": ["内容", "卡片"], "content": ["内容", "要点", "卡片"],
    "summary": ["内容", "要点"], "end": ["封面"],
    "statement": ["封面", "章节"], "overview": ["内容", "要点", "卡片"],
    "kpi": ["对比", "数据", "内容"], "roadmap": ["流程", "内容"],
}
def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_json(path, label):
    try:
        with open(path, encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"[make_prompt] {label} 无法读取：{exc}")


def prompt_section(md, heading, label):
    pattern = rf"##\s*{re.escape(heading)}.*?```\n(.*?)```"
    match = re.search(pattern, md, re.S)
    if not match:
        sys.exit(f"[make_prompt] {label} 缺少“{heading}”代码块")
    return match.group(1).strip()


def parse_palette(md):
    """返回 (token映射, 配色描述段)，同时支持旧 Token 与 v2.3 语义 Token。"""
    tokens = {}
    for line in md.splitlines():
        match = re.match(r"\|\s*`\{(\w+)\}`\s*\|", line)
        if not match:
            continue
        cells = line.split("|")
        if len(cells) < 5:
            continue
        tok = match.group(1)
        hexv = cells[2].replace("`", "").strip()
        desc = cells[3].strip()
        name = desc.split("/")[0].strip()
        tokens["{%s}" % tok] = f"{name}({hexv.split('→')[0].strip()})"
    m = re.search(r"##\s*提示词配色描述段.*?```\n(.*?)```", md, re.S)
    scheme = m.group(1).strip() if m else ""
    if not tokens or not scheme:
        sys.exit("[make_prompt] 配色文件解析失败：缺少 Token 表或提示词配色描述段")
    return tokens, scheme


def pick_style_skeleton(style_md):
    """优先读取 v2.3 deck-wide 风格骨架；旧风格返回 None 进入兼容路径。"""
    match = re.search(r"##\s*风格提示词骨架.*?```\n(.*?)```", style_md, re.S)
    return match.group(1).strip() if match else None


def pick_template(style_md, template):
    """v2.2 兼容：从旧风格文件中选择页面模板代码块。"""
    sections = re.findall(r"###\s*([^\n]+)\n+```\n(.*?)```", style_md, re.S)
    if not sections:
        sys.exit("[make_prompt] 风格文件中未找到 '### 标题 + 代码块' 形式的页面模板")
    for kw in TEMPLATE_KEYWORDS.get(template, ["内容"]):
        for title, block in sections:
            if kw in title:
                return block.strip()
    return sections[-1][1].strip()  # 兜底：最后一个模板（通常是内容页）


def load_visual_layers(design, plan, page, style_md):
    page_dir = os.path.join(design, "page-types")
    industry_dir = os.path.join(design, "industries")
    page_config = read_json(os.path.join(page_dir, "index.json"), "页面类型索引")
    industry_config = read_json(os.path.join(industry_dir, "index.json"), "行业视觉索引")

    page_type = page.get("page_type") or page_config.get("template_map", {}).get(
        page.get("template", "content")
    )
    page_entry = page_config.get("page_types", {}).get(page_type)
    if not page_entry:
        sys.exit(f"[make_prompt] 未登记页面类型：{page_type}")

    industry = plan.get("industry") or "general"
    industry_entry = industry_config.get("profiles", {}).get(industry)
    if not industry_entry:
        sys.exit(f"[make_prompt] 未登记行业视觉修饰：{industry}")

    page_md = read(os.path.join(page_dir, page_entry["file"]))
    industry_md = read(os.path.join(industry_dir, industry_entry["file"]))
    page_fragment = prompt_section(page_md, "提示词片段", f"页面类型 {page_type}")
    industry_fragment = prompt_section(
        industry_md, "提示词片段", f"行业视觉修饰 {industry}"
    )

    style_skeleton = pick_style_skeleton(style_md)
    if style_skeleton is None:
        style_skeleton = pick_template(style_md, page.get("template", "content"))

    page["page_type"] = page_type
    plan["industry"] = industry
    return style_skeleton, page_fragment, industry_fragment


def apply_visual_tokens(text, scheme, tokens):
    text = text.replace("[COLOR_SCHEME]", scheme)
    for token, value in tokens.items():
        text = text.replace(token, value)
    unresolved = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_]*\}", text)))
    if unresolved:
        sys.exit(f"[make_prompt] 未解析的视觉 Token：{unresolved}")
    return text


def governance_prompt(design, plan):
    governance, _compatibility = design_governance.load_design(design)
    profile = governance["style_profiles"][plan["style"]]
    rules = governance["deck_rules"]
    typography = profile["typography"]
    spatial = rules["spatial_consistency"]
    lines = [
        "DECK-WIDE VISUAL GOVERNANCE:",
        f"- Density range: {profile['density'][0]}-{profile['density'][1]}/10.",
        f"- Variance range: {profile['variance'][0]}-{profile['variance'][1]}/10.",
        f"- Shape lock: {profile['shape']}.",
        f"- Radius lock: {profile['radius']}.",
        f"- Shadow policy: {profile['shadow']}.",
        f"- Material precedence: {profile['material']}.",
        f"- Image policy: {profile['image']}.",
        f"- Annotation policy: {profile['annotation']}.",
        f"- Use no more than {profile['micro_label_budget']} micro-labels on one slide.",
        f"- Use at most {rules['max_focus_objects_per_page']} decisive focal object.",
        "- Use fill/line colors for focus and status; use the corresponding "
        "*_TEXT role for small text.",
        f"- Do not repeat one layout family on more than "
        f"{rules['max_consecutive_layout_family']} consecutive slides.",
        "- Keep these locks across every page type in the deck.",
        "",
        "TYPOGRAPHY GOVERNANCE:",
        f"- Typeface family budget: {typography['family_budget']}.",
        f"- Family policy: {typography['family_policy']}.",
        f"- Type hierarchy: {typography['hierarchy_levels']} levels.",
        f"- Display type: {typography['display']}.",
        f"- Body type: {typography['body']}.",
        f"- Small-text policy: {typography['small_text']}.",
        "",
        "SPATIAL CONSISTENCY:",
        f"- Stable title axis: {spatial['title_axis']}.",
        f"- Semantic anchor: {spatial['semantic_anchor']}.",
        f"- Transition anchor: {spatial['transition_anchor']}.",
    ]
    material_layers = profile.get("material_layers")
    if material_layers:
        lines.extend(
            (
                "",
                "MATERIAL LAYER LIMITS:",
                "- Maximum translucent layers: "
                f"{material_layers['max_translucent_layers']}.",
                "- Glass-on-glass: "
                + (
                    "allowed."
                    if material_layers["glass_on_glass"]
                    else "forbidden."
                ),
                "- Solid text backing: "
                + (
                    "required."
                    if material_layers["solid_text_backing"]
                    else "optional."
                ),
                "- Dense-page material policy: "
                f"{material_layers['dense_page_policy']}.",
            )
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--page", required=True)
    ap.add_argument("--design", default=os.path.join(REPO, "references", "design"))
    ap.add_argument("--print", action="store_true", dest="echo")
    args = ap.parse_args()

    plan_path = os.path.join(WS, "plan.json")
    with open(plan_path, encoding="utf-8") as stream:
        plan = json.load(stream)
    try:
        project_contract.normalize_plan(plan)
    except project_contract.ContractError as exc:
        sys.exit(f"[make_prompt] 项目契约无效：{exc}")
    if not plan.get("palette") or not plan.get("style"):
        sys.exit("[make_prompt] plan.json 未锁定 palette/style，先完成 Phase 4（plan_tool.py design）")
    compatibility_path = os.path.join(args.design, "compatibility.json")
    try:
        with open(compatibility_path, encoding="utf-8") as stream:
            compatibility = json.load(stream)
        rule = compatibility["combinations"][plan["palette"]][plan["style"]]
    except (OSError, KeyError, json.JSONDecodeError):
        sys.exit(f"[make_prompt] 未登记设计组合：{plan['palette']} × {plan['style']}")
    if rule.get("status") == "blocked":
        sys.exit(f"[make_prompt] 禁止设计组合：{plan['palette']} × {plan['style']}："
                 f"{rule.get('reason', '不兼容')}")
    page = next((p for p in plan["pages"] if p["id"] == args.page), None)
    if not page:
        sys.exit(f"[make_prompt] 找不到页面 {args.page}")
    if page.get("reuse_mode") == "exact_asset":
        print(
            f"[make_prompt] {page['id']} 使用 exact_asset 复用 "
            f"{page['reused_from']}，无需生成独立提示词"
        )
        return
    findings = project_contract.lint_pages(plan, page_ids={page["id"]})
    errors = [item for item in findings if item["severity"] == "error"]
    if errors:
        sys.exit(
            "[make_prompt] 项目契约检查失败：\n"
            + project_contract.format_findings(errors)
        )
    warnings = [item for item in findings if item["severity"] == "warning"]
    if warnings:
        print(
            "[make_prompt] 项目契约警告：\n"
            + project_contract.format_findings(warnings),
            file=sys.stderr,
        )

    palette_md = read(os.path.join(args.design, "palettes", plan["palette"] + ".md"))
    style_path = os.path.join(args.design, "styles", plan["style"] + ".md")
    style_md = read(style_path)
    constraints_md = read(os.path.join(REPO, "references", "constraints.md"))
    m = re.search(r"##\s*提示词附加段.*?```\n(.*?)```", constraints_md, re.S)
    constraints = m.group(1).strip() if m else ""

    tokens, scheme = parse_palette(palette_md)
    style_layer, page_layer, industry_layer = load_visual_layers(
        args.design, plan, page, style_md
    )
    governance_layer = governance_prompt(args.design, plan)
    tpl = "\n\n".join(
        (style_layer, page_layer, industry_layer, governance_layer)
    )
    tpl = apply_visual_tokens(tpl, scheme, tokens)
    for ph in ("[主题]", "[标题]", "[案例标题]"):
        tpl = tpl.replace(ph, page["title"])
    tpl = tpl.replace("[副标题]", page.get("subtitle") or page["title"])

    content = [f"\nPage content (use EXACTLY this text, no additions):",
               f"- Title: {page['title']}"]
    if page.get("subtitle"):
        content.append(f"- Subtitle: {page['subtitle']}")
    for pt in page.get("points", []):
        content.append(f"- Point: {pt}")
    if page.get("layout_hint"):
        content.append(f"- Layout hint: {page['layout_hint']}")

    contract_block = project_contract.prompt_contract_block(plan, page)
    prompt_parts = [tpl, "\n".join(content)]
    if contract_block:
        prompt_parts.append(contract_block)
    prompt_parts.append(constraints)
    prompt = "\n\n".join(prompt_parts)
    project_contract.record_prompt_hash(plan, page)

    out = os.path.join(WS, page["prompt_file"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(prompt)

    refs = sorted(
        os.path.join(args.design, "styles", plan["style"], fn)
        for fn in os.listdir(os.path.join(args.design, "styles", plan["style"]))
        if fn.startswith("ref-")) if os.path.isdir(
        os.path.join(args.design, "styles", plan["style"])) else []

    changed = False
    if page["status"] == "pending":
        page["status"] = "prompted"
        changed = True
    if page.get("page_type") or plan.get("industry"):
        changed = True
    if changed:
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

    print(f"[make_prompt] 已生成 {out}")
    if refs:
        print("[make_prompt] 垫图参考（随生图请求一并提交）:")
        for r in refs:
            print("  " + r)
    if args.echo:
        print("-" * 60 + "\n" + prompt)


if __name__ == "__main__":
    main()
