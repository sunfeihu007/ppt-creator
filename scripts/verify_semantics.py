#!/usr/bin/env python3
"""Verify optional OCR text against the PPT Creator project contract."""

import argparse
import json
import os
from pathlib import Path
import re
import sys

import project_contract


WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")


def normalized_text(value):
    return re.sub(r"\s+", "", value or "")


def finding(severity, page_id, rule_id, message):
    return {
        "severity": severity,
        "page": page_id,
        "rule_id": rule_id,
        "message": message,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ocr-dir", default=os.path.join(WS, "qa", "ocr")
    )
    parser.add_argument(
        "--report", default=os.path.join(WS, "qa", "semantic-report.json")
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--require-ocr", action="store_true")
    args = parser.parse_args()

    plan_path = os.path.join(WS, "plan.json")
    try:
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
        project_contract.normalize_plan(plan)
    except (OSError, json.JSONDecodeError, project_contract.ContractError) as exc:
        sys.exit(f"[verify_semantics] 无法读取有效计划：{exc}")

    ocr_dir = Path(args.ocr_dir)
    findings = []
    checked = []
    skipped = []
    for page in plan["pages"]:
        source = project_contract.effective_page(plan, page)
        ocr_path = ocr_dir / f"{source['id']}.txt"
        if not ocr_path.exists():
            skipped.append(page["id"])
            print(f"[verify_semantics] {page['id']} SKIPPED（无 OCR 文本）")
            if args.require_ocr:
                findings.append(
                    finding(
                        "error",
                        page["id"],
                        "OCR-MISSING",
                        f"缺少 OCR 文本：{ocr_path}",
                    )
                )
            continue
        text = ocr_path.read_text(encoding="utf-8")
        checked.append(page["id"])
        findings.extend(
            project_contract.lint_pages(
                plan,
                page_ids={page["id"]},
                text_overrides={page["id"]: text},
                strict=args.strict,
            )
        )
        title = normalized_text(page.get("title", ""))
        if title and title not in normalized_text(text):
            findings.append(
                finding(
                    "error" if args.strict else "warning",
                    page["id"],
                    "OCR-TITLE",
                    f"OCR 文本未找到完整标题：{page['title']}",
                )
            )

    errors = [item for item in findings if item["severity"] == "error"]
    report = {
        "status": "failed" if errors else "passed",
        "strict": args.strict,
        "require_ocr": args.require_ocr,
        "checked_pages": checked,
        "skipped_pages": skipped,
        "findings": findings,
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for item in findings:
        print(
            f"[{item['severity'].upper()}] {item['page']} "
            f"{item['rule_id']}: {item['message']}"
        )
    if errors:
        sys.exit(
            f"[verify_semantics] FAILED（{len(errors)} 个错误）；"
            f"报告：{report_path}"
        )
    print(
        f"[verify_semantics] PASSED（检查 {len(checked)} 页，"
        f"跳过 {len(skipped)} 页）；报告：{report_path}"
    )


if __name__ == "__main__":
    main()
