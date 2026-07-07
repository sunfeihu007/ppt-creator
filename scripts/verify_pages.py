#!/usr/bin/env python3
"""页面产物自动校验：存在性 / 可打开 / 16:9比例 / 最低分辨率。

用法: verify_pages.py [--min-width 1280] [--pages P01,P02]
退出码: 0=全部通过, 1=有失败项（失败页需重新生成）。
注意：本脚本只做机器可查项；乱码/截断/风格漂移仍需 AI 目检（constraints.md 检查清单）。
"""
import argparse
import json
import os
import sys

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-width", type=int, default=1280)
    ap.add_argument("--pages", help="只校验指定页，逗号分隔")
    args = ap.parse_args()

    from PIL import Image
    plan = json.load(open(os.path.join(WS, "plan.json"), encoding="utf-8"))
    only = set(args.pages.split(",")) if args.pages else None
    failures = []
    for p in plan["pages"]:
        if only and p["id"] not in only:
            continue
        path = os.path.join(WS, p["image"])
        problem = None
        if not os.path.exists(path):
            problem = "文件不存在"
        else:
            try:
                im = Image.open(path)
                im.load()
                w, h = im.size
                if abs(w / h - 16 / 9) > 0.02:
                    problem = f"比例异常 {w}x{h}（应16:9，可用 gen_image 自动裁切）"
                elif w < args.min_width:
                    problem = f"分辨率过低 {w}x{h}（最低宽 {args.min_width}）"
            except Exception as e:  # noqa: BLE001
                problem = f"无法打开: {str(e)[:80]}"
        mark = "✗ " + problem if problem else "✓"
        print(f"  {p['id']:6s} [{p['status']:9s}] {mark}")
        if problem:
            failures.append(p["id"])
    if failures:
        print(f"[verify] FAILED: {failures} —— 这些页面需要重新生成")
        sys.exit(1)
    print(f"[verify] PASSED（{len(plan['pages']) if not only else len(only)} 页机器校验通过）。"
          "别忘了 AI 目检：乱码/截断/风格漂移。")


if __name__ == "__main__":
    main()
