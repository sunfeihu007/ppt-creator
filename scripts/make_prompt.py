#!/usr/bin/env python3
"""提示词拼装器：风格模板骨架 + 配色描述段 + 页面内容 + 全局约束。

AI 只负责在 plan.json 里填好每页的 title/points/layout_hint，
提示词的固定部分（风格、配色、禁止项）全部由本脚本从设计系统拼装，
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

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 页面 template -> 风格文件中模板小节标题的关键词（按优先级）
TEMPLATE_KEYWORDS = {
    "cover": ["封面"], "toc": ["目录"], "transition": ["封面"],
    "arch": ["架构"], "flow": ["流程"], "compare": ["对比", "流程"],
    "case": ["内容", "卡片"], "content": ["内容", "要点", "卡片"],
    "summary": ["内容", "要点"], "end": ["封面"],
}
EXTRA_HINT = {
    "transition": "This is a SECTION TRANSITION slide: reuse the cover's visual language "
                  "but simpler — big section number + section title, low density.",
    "end": "This is the CLOSING slide: reuse the cover's visual language, "
           "short thank-you style title, very low density.",
    "summary": "This is the SUMMARY slide: recap layout, medium-low density.",
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_palette(md):
    """返回 (token映射, 配色描述段)。token映射: {PRIMARY} -> '活力橙(#E87818)'"""
    tokens = {}
    for m in re.finditer(
            r"\|\s*`\{(\w+)\}`\s*\|\s*`?([^|`]+?)`?\s*\|\s*([^|]+?)\s*\|", md):
        tok, hexv, desc = m.group(1), m.group(2).strip(), m.group(3).strip()
        name = desc.split("/")[0].strip()
        tokens["{%s}" % tok] = f"{name}({hexv.split('→')[0].strip()})"
    m = re.search(r"##\s*提示词配色描述段.*?```\n(.*?)```", md, re.S)
    scheme = m.group(1).strip() if m else ""
    if not tokens or not scheme:
        sys.exit("[make_prompt] 配色文件解析失败：缺少 Token 表或提示词配色描述段")
    return tokens, scheme


def pick_template(style_md, template):
    """从风格文件中选出与页面 template 匹配的提示词模板代码块。"""
    sections = re.findall(r"###\s*([^\n]+)\n+```\n(.*?)```", style_md, re.S)
    if not sections:
        sys.exit("[make_prompt] 风格文件中未找到 '### 标题 + 代码块' 形式的页面模板")
    for kw in TEMPLATE_KEYWORDS.get(template, ["内容"]):
        for title, block in sections:
            if kw in title:
                return block.strip()
    return sections[-1][1].strip()  # 兜底：最后一个模板（通常是内容页）


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--page", required=True)
    ap.add_argument("--design", default=os.path.join(REPO, "references", "design"))
    ap.add_argument("--print", action="store_true", dest="echo")
    args = ap.parse_args()

    plan = json.load(open(os.path.join(WS, "plan.json"), encoding="utf-8"))
    if not plan.get("palette") or not plan.get("style"):
        sys.exit("[make_prompt] plan.json 未锁定 palette/style，先完成 Phase 4（plan_tool.py design）")
    page = next((p for p in plan["pages"] if p["id"] == args.page), None)
    if not page:
        sys.exit(f"[make_prompt] 找不到页面 {args.page}")

    palette_md = read(os.path.join(args.design, "palettes", plan["palette"] + ".md"))
    style_path = os.path.join(args.design, "styles", plan["style"] + ".md")
    style_md = read(style_path)
    constraints_md = read(os.path.join(REPO, "references", "constraints.md"))
    m = re.search(r"##\s*提示词附加段.*?```\n(.*?)```", constraints_md, re.S)
    constraints = m.group(1).strip() if m else ""

    tokens, scheme = parse_palette(palette_md)
    tpl = pick_template(style_md, page["template"])
    tpl = tpl.replace("[COLOR_SCHEME]", scheme)
    for tok, val in tokens.items():
        tpl = tpl.replace(tok, val)
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
    if page["template"] in EXTRA_HINT:
        content.append("- " + EXTRA_HINT[page["template"]])

    prompt = tpl + "\n" + "\n".join(content) + "\n\n" + constraints

    out = os.path.join(WS, page["prompt_file"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(prompt)

    refs = sorted(
        os.path.join(args.design, "styles", plan["style"], fn)
        for fn in os.listdir(os.path.join(args.design, "styles", plan["style"]))
        if fn.startswith("ref-")) if os.path.isdir(
        os.path.join(args.design, "styles", plan["style"])) else []

    if page["status"] == "pending":
        page["status"] = "prompted"
        with open(os.path.join(WS, "plan.json"), "w", encoding="utf-8") as f:
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
