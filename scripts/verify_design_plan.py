#!/usr/bin/env python3
"""Preflight a PPT plan for palette/style compatibility and deck rhythm."""
import argparse
import json
import os
from pathlib import Path
import sys

import design_governance


def main():
    workspace = Path(os.environ.get("PPTC_WORKSPACE", "./ppt_workspace"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default=str(workspace / "plan.json"))
    parser.add_argument(
        "--design", default=str(design_governance.DEFAULT_DESIGN)
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", dest="report_path")
    args = parser.parse_args()

    try:
        with Path(args.plan).open(encoding="utf-8") as stream:
            plan = json.load(stream)
        findings = design_governance.lint_plan(plan, design=args.design)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"[verify_design_plan] 无法检查：{exc}", file=sys.stderr)
        return 2

    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    passed = errors == 0 and (not args.strict or warnings == 0)
    report = {
        "passed": passed,
        "strict": args.strict,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    }
    if args.report_path:
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if findings:
        print(design_governance.format_findings(findings))
    if passed and not warnings:
        print("[verify_design_plan] PASSED")
    elif passed:
        print(f"[verify_design_plan] PASSED WITH {warnings} WARNING(S)")
    else:
        print(
            f"[verify_design_plan] FAILED: {errors} error(s), {warnings} warning(s)"
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
