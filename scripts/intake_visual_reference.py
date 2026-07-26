#!/usr/bin/env python3
"""Create a non-promotable intake record from visual reference screenshots.

The command records provenance, file hashes, dimensions, the user's stated taste,
and a conservative classification. It never copies source pixels into the Skill
and never edits the live palette/style registries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image


VALID_PAGE_TYPES = {
    "cover",
    "toc",
    "section",
    "overview",
    "architecture",
    "flow",
    "detail",
    "compare-kpi",
    "case",
    "roadmap",
    "closing",
}
VALID_SCOPES = {"auto", "palette", "style", "layout", "industry"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_source(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"参考图不存在：{path}")
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format
    except OSError as exc:
        raise ValueError(f"参考图无法读取：{path}: {exc}") from exc
    return {
        "path": str(path),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "format": image_format,
        "embedded": False,
    }


def classify(scope, source_count, page_types):
    if scope != "auto":
        return f"{scope}-candidate"
    if source_count == 1:
        return "palette-or-layout"
    if source_count >= 4 and len(set(page_types)) >= 4:
        return "style-candidate"
    return "visual-candidate"


def build_proposal(args):
    sources = [inspect_source(path) for path in args.source]
    page_types = list(dict.fromkeys(args.page_type))
    invalid_page_types = sorted(set(page_types) - VALID_PAGE_TYPES)
    if invalid_page_types:
        raise ValueError(f"未知 page_type：{invalid_page_types}")

    classification = classify(args.scope, len(sources), page_types)
    style_intake_complete = (
        classification == "style-candidate"
        and len(sources) >= 4
        and len(page_types) >= 4
    )
    intake_complete = bool(sources and args.liked)
    if classification == "style-candidate":
        intake_complete = intake_complete and style_intake_complete

    warnings = []
    if not args.source_url:
        warnings.append("缺少原始网址；后续必须补充来源或注明仅有本地文件")
    if len(sources) == 1:
        warnings.append("单张截图只能证明候选配色或单页布局，不能证明整套风格")
    if args.scope == "style" and not style_intake_complete:
        warnings.append("完整风格至少需要 4 张参考图和 4 种不同 page_type")

    return {
        "schema_version": 1,
        "status": "candidate",
        "scope_requested": args.scope,
        "classification": classification,
        "intake_complete": intake_complete,
        "promotion_ready": False,
        "registry_mutation_allowed": False,
        "source_url": args.source_url or None,
        "liked": args.liked,
        "page_types": page_types,
        "sources": sources,
        "transferable_dimensions": [
            "semantic color roles",
            "typographic hierarchy",
            "grid and spacing",
            "material hierarchy",
            "image treatment",
            "static spatial anchors",
        ],
        "non_transferable_dimensions": [
            "client names and logos",
            "copyrighted source pixels",
            "unverified data and metrics",
            "website hover, gesture, motion, and responsive behavior",
        ],
        "warnings": warnings,
        "required_next_steps": [
            "human or vision-model visual extraction",
            "existing palette/style overlap review",
            "16 semantic-token and contrast validation",
            "cross-industry generality review",
            "neutral no-text no-brand reference generation",
            "cover, architecture, and detail sample review",
            "explicit human approval before registry promotion",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--liked", action="append", required=True)
    parser.add_argument("--scope", choices=sorted(VALID_SCOPES), default="auto")
    parser.add_argument("--page-type", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        proposal = build_proposal(args)
    except ValueError as exc:
        print(f"[intake_visual_reference] {exc}", file=sys.stderr)
        return 1

    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[intake_visual_reference] {proposal['classification']} -> {output}; "
        "candidate only, live registries unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
