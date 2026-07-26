#!/usr/bin/env python3
"""PPTX 组装器：gate检查 → 图片压缩 → 按plan顺序组装 → 注入演讲者备注。

用法: build_ppt.py [--allow-generated] [--no-compress] [--out 路径]
gate: 默认要求全部页面 status=approved（--allow-generated 放宽到 generated，仅调试用）。
压缩: >2MB 的 PNG 转 JPEG(q85)，可缩小5-20倍体积，便于分发。
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

import design_governance
import project_contract

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
STATUS_ORDER = ["pending", "prompted", "generating", "generated", "qa_passed", "approved"]


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-generated", action="store_true")
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    from PIL import Image
    from pptx import Presentation
    from pptx.util import Inches

    plan_path = os.path.join(WS, "plan.json")
    plan = json.load(open(plan_path, encoding="utf-8"))
    try:
        project_contract.normalize_plan(plan)
    except project_contract.ContractError as exc:
        sys.exit(f"[build] 项目契约无效：{exc}")
    design_findings = design_governance.lint_plan(plan)
    design_errors = [
        item for item in design_findings if item["severity"] == "error"
    ]
    if design_errors:
        sys.exit(
            "[build] DESIGN GATE FAILED：\n"
            + design_governance.format_findings(design_errors)
        )
    design_warnings = [
        item for item in design_findings if item["severity"] == "warning"
    ]
    if design_warnings:
        print(
            "[build] 视觉治理警告：\n"
            + design_governance.format_findings(design_warnings),
            file=sys.stderr,
        )
    lint_errors = [
        item
        for item in project_contract.lint_pages(plan)
        if item["severity"] == "error"
    ]
    if lint_errors:
        sys.exit(
            "[build] SEMANTIC GATE FAILED：\n"
            + project_contract.format_findings(lint_errors)
        )
    stale = project_contract.sync_findings(plan)
    if stale:
        details = ", ".join(
            f"{item['page']}({item['reason']})" for item in stale
        )
        sys.exit(f"[build] STALE：{details}")

    # ---- GATE：拒绝组装未完成的PPT（防跳步的最后一道闸）----
    need = "generated" if args.allow_generated else "approved"
    lvl = STATUS_ORDER.index(need)
    bad = [f"{p['id']}({p['status']})" for p in plan["pages"]
           if STATUS_ORDER.index(p["status"]) < lvl]
    if bad:
        sys.exit(f"[build] GATE FAILED —— 以下页面未达 {need}，按七步流程先完成它们:\n  "
                 + ", ".join(bad))
    missing_notes = [p["id"] for p in plan["pages"] if not p.get("notes", "").strip()]
    if missing_notes:
        print(f"[build] 警告：以下页面缺演讲者备注: {missing_notes}")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    total_in = total_out = 0
    source_images = []
    for p in plan["pages"]:
        source_page = project_contract.effective_page(plan, p)
        image_path = project_contract.effective_image(plan, p)
        path = os.path.join(WS, image_path)
        size_in = os.path.getsize(path)
        total_in += size_in
        stream = path
        with Image.open(path) as source_image:
            width, height = source_image.size
            source_format = source_image.format or "UNKNOWN"
        embedded_media = source_format
        if not args.no_compress and size_in > 2 * 1024 * 1024:
            im = Image.open(path).convert("RGB")
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=85)
            buf.seek(0)
            stream = buf
            total_out += buf.getbuffer().nbytes
            embedded_media = "JPEG"
        else:
            total_out += size_in
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(stream, 0, 0,
                                 width=prs.slide_width, height=prs.slide_height)
        if p.get("notes"):
            slide.notes_slide.notes_text_frame.text = p["notes"]
        source_images.append(
            {
                "page": p["id"],
                "resolved_from": source_page["id"],
                "file": image_path,
                "width": width,
                "height": height,
                "sha256": file_sha256(path),
                "embedded_media": embedded_media,
            }
        )

    topic = re.sub(r'[\\/:*?"<>|]', "_", plan.get("topic") or "presentation")
    out = args.out or os.path.join(WS, "output", f"{topic}.pptx")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)
    project_contract.export_outline(
        plan, os.path.join(WS, "final_outline.md")
    )
    mb = os.path.getsize(out) / 1048576
    manifest = {
        "schema_version": "2.4",
        "delivery_mode": plan["delivery_mode"],
        "pptx": {
            "file": os.path.abspath(out),
            "bytes": os.path.getsize(out),
            "pages": len(plan["pages"]),
        },
        "notes_count": sum(
            1 for page in plan["pages"] if page.get("notes", "").strip()
        ),
        "source_images": source_images,
    }
    manifest_path = os.path.join(WS, "output", "artifact_manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    with open(plan_path, "w", encoding="utf-8") as stream:
        json.dump(plan, stream, ensure_ascii=False, indent=2)
    print(f"[build] ✓ {out}")
    print(f"[build] {len(plan['pages'])} 页 | 图片 {total_in/1048576:.0f}MB -> "
          f"约{total_out/1048576:.0f}MB | 成品 {mb:.1f}MB")
    print(
        f"[build] 最终大纲: {os.path.join(WS, 'final_outline.md')} | "
        f"交付清单: {manifest_path}"
    )


if __name__ == "__main__":
    main()
