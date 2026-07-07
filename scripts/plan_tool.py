#!/usr/bin/env python3
"""plan.json 状态管理工具 —— 七步流程的唯一事实来源。

用法:
  plan_tool.py init --file draft_plan.json      # Phase 3: 由草稿创建 plan.json
  plan_tool.py status                           # 打印进度与下一步建议
  plan_tool.py design --palette X --style Y --provider Z   # Phase 4 写入设计组合
  plan_tool.py phase --name 4_design --status done
  plan_tool.py page --id P01 --status generated [--image path] [--notes "..."]
  plan_tool.py check --min-status approved      # gate: 不满足则退出码1

环境变量 PPTC_WORKSPACE 可改工作目录（默认 ./ppt_workspace）。
"""
import argparse
import json
import os
import sys

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
PLAN = os.path.join(WS, "plan.json")
PHASES = ["1_outline", "2_content", "3_pages", "4_design",
          "5_framework", "6_content_pages", "7_assembly"]
PAGE_STATUS = ["pending", "prompted", "generated", "approved"]
TEMPLATES = ["cover", "toc", "transition", "content", "arch",
             "flow", "compare", "case", "summary", "end"]

# hud-frame 只能配深色配色；深色配色只能配 hud-frame
DARK_PALETTES = {"deep-space"}
DARK_ONLY_STYLES = {"hud-frame"}


def load():
    if not os.path.exists(PLAN):
        sys.exit(f"[plan_tool] {PLAN} 不存在。请先完成 Phase 1-3 并执行 init。")
    with open(PLAN, encoding="utf-8") as f:
        return json.load(f)


def save(plan):
    os.makedirs(WS, exist_ok=True)
    with open(PLAN, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)


def cmd_init(args):
    with open(args.file, encoding="utf-8") as f:
        draft = json.load(f)
    if os.path.exists(PLAN) and not args.force:
        sys.exit(f"[plan_tool] {PLAN} 已存在，如需覆盖加 --force")
    pages = []
    for i, p in enumerate(draft.get("pages", []), 1):
        pid = p.get("id") or f"P{i:02d}"
        tpl = p.get("template", "content")
        if tpl not in TEMPLATES:
            sys.exit(f"[plan_tool] 页面 {pid} 的 template '{tpl}' 非法，可选: {TEMPLATES}")
        pages.append({
            "id": pid, "template": tpl,
            "title": p.get("title", ""), "subtitle": p.get("subtitle", ""),
            "points": p.get("points", []), "layout_hint": p.get("layout_hint", ""),
            "notes": p.get("notes", ""), "status": "pending",
            "prompt_file": f"prompts/{pid}.txt", "image": f"pages/{pid}.png",
        })
    if not pages:
        sys.exit("[plan_tool] 草稿中没有 pages")
    plan = {
        "topic": draft.get("topic", ""), "audience": draft.get("audience", ""),
        "palette": None, "style": None, "provider": None,
        "phases": {ph: ("done" if ph in ("1_outline", "2_content", "3_pages") else "pending")
                   for ph in PHASES},
        "pages": pages,
    }
    save(plan)
    for sub in ("prompts", "pages", "pages/history", "output"):
        os.makedirs(os.path.join(WS, sub), exist_ok=True)
    print(f"[plan_tool] 已创建 {PLAN}（{len(pages)} 页），Phase 1-3 标记为 done")


def cmd_design(args):
    plan = load()
    style, palette = args.style, args.palette
    if (style in DARK_ONLY_STYLES) != (palette in DARK_PALETTES):
        sys.exit(f"[plan_tool] 非法组合：{palette} × {style}。"
                 f"hud-frame 只能配深色配色（{DARK_PALETTES}），反之亦然。")
    plan.update({"palette": palette, "style": style, "provider": args.provider})
    save(plan)
    print(f"[plan_tool] 设计组合已锁定: {palette} × {style} × {args.provider}")


def cmd_provider(args):
    plan = load()
    old = plan.get("provider")
    plan["provider"] = args.name
    save(plan)
    print(f"[plan_tool] 生图后端: {old} -> {args.name}")
    if old and old != args.name:
        done = [p["id"] for p in plan["pages"]
                if p["status"] in ("generated", "approved")]
        if done:
            print(f"[plan_tool] 提醒：{len(done)} 页已用 {old} 生成（{done[:6]}…）。"
                  "混用后端画风会有差异，建议重生成这些页面以保持整套一致。")


def cmd_phase(args):
    plan = load()
    if args.name not in PHASES:
        sys.exit(f"[plan_tool] 未知 phase: {args.name}，可选: {PHASES}")
    if args.status == "done":
        idx = PHASES.index(args.name)
        for prev in PHASES[:idx]:
            if plan["phases"][prev] != "done":
                sys.exit(f"[plan_tool] 禁止跳步：{prev} 尚未 done，不能完成 {args.name}")
        if args.name in ("5_framework", "6_content_pages"):
            fw = {"cover", "toc", "transition", "summary", "end"}
            need_fw = args.name == "5_framework"
            bad = [p["id"] for p in plan["pages"]
                   if ((p["template"] in fw) == need_fw) and p["status"] != "approved"]
            if bad:
                sys.exit(f"[plan_tool] 禁止跳步：以下页面未 approved: {bad}")
    plan["phases"][args.name] = args.status
    save(plan)
    print(f"[plan_tool] phase {args.name} -> {args.status}")


def cmd_page(args):
    plan = load()
    for p in plan["pages"]:
        if p["id"] == args.id:
            if args.status:
                if args.status not in PAGE_STATUS:
                    sys.exit(f"[plan_tool] 非法状态 {args.status}，可选: {PAGE_STATUS}")
                p["status"] = args.status
            if args.image:
                p["image"] = args.image
            if args.notes is not None:
                p["notes"] = args.notes
            save(plan)
            print(f"[plan_tool] page {args.id}: status={p['status']}")
            return
    sys.exit(f"[plan_tool] 找不到页面 {args.id}")


def cmd_status(_args):
    plan = load()
    print(f"主题: {plan['topic']}  设计: {plan.get('palette')} × {plan.get('style')}"
          f" × {plan.get('provider')}")
    for ph in PHASES:
        print(f"  {ph:18s} {plan['phases'][ph]}")
    counts = {}
    for p in plan["pages"]:
        counts[p["status"]] = counts.get(p["status"], 0) + 1
    print(f"页面({len(plan['pages'])}): " +
          " ".join(f"{k}={v}" for k, v in counts.items()))
    nxt = next((ph for ph in PHASES if plan["phases"][ph] != "done"), None)
    if nxt:
        print(f"下一步: 完成 {nxt}" +
              ("（先读 references/phases/ 对应文件）" if nxt != "7_assembly" else ""))
        todo = [p["id"] for p in plan["pages"] if p["status"] != "approved"][:8]
        if nxt in ("5_framework", "6_content_pages") and todo:
            print(f"待处理页面: {todo}")
    else:
        print("全部完成 ✓")


def cmd_check(args):
    plan = load()
    lvl = PAGE_STATUS.index(args.min_status)
    bad = [f"{p['id']}({p['status']})" for p in plan["pages"]
           if PAGE_STATUS.index(p["status"]) < lvl]
    if bad:
        print(f"[plan_tool] GATE FAILED，以下页面未达 {args.min_status}: {', '.join(bad)}")
        sys.exit(1)
    print(f"[plan_tool] GATE PASSED（全部页面 >= {args.min_status}）")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--file", required=True)
    s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("design")
    s.add_argument("--palette", required=True); s.add_argument("--style", required=True)
    s.add_argument("--provider", required=True, choices=["gemini", "codex", "codex-builtin"])
    s.set_defaults(fn=cmd_design)
    s = sub.add_parser("provider")
    s.add_argument("--name", required=True, choices=["codex", "gemini", "codex-builtin"])
    s.set_defaults(fn=cmd_provider)
    s = sub.add_parser("phase")
    s.add_argument("--name", required=True)
    s.add_argument("--status", required=True, choices=["pending", "done"])
    s.set_defaults(fn=cmd_phase)
    s = sub.add_parser("page")
    s.add_argument("--id", required=True); s.add_argument("--status")
    s.add_argument("--image"); s.add_argument("--notes"); s.set_defaults(fn=cmd_page)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("check")
    s.add_argument("--min-status", default="approved", choices=PAGE_STATUS)
    s.set_defaults(fn=cmd_check)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
