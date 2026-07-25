#!/usr/bin/env python3
"""生图执行器：脚本后端与原生工具产物导入，带重试与16:9裁切。

默认路由:
  - AGY 内使用原生 generate_image，再用 --import-file 导入；
  - Codex 内使用原生 image_gen，再用 --import-file 导入；
  - 其他客户端通过 Gemini API，默认 gemini-3.1-flash-image。

显式兼容桥:
  agy/cli   : 实验性的 ``agy -p`` 调用，必须先通过 preflight；
  codex/cli : ``codex exec`` 调用；
  gemini/api: Gemini REST API，需要 GEMINI_API_KEY 或 GOOGLE_API_KEY。

provider/transport/model 在样张前锁入 plan.json。锁定后显式参数不得绕过，
也不能用 both 混用模型；正式切换必须先用 plan_tool.py provider 更新计划。

用法:
  gen_image.py --page P01 [--provider auto|agy|codex|gemini|both]
               [--transport native|cli|api] [--import-file PATH]
               [--pick codex|gemini] [--no-refs]
               [--max-attempts 8] [--no-state]
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.error

import image_providers


WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVIDER_TRANSPORTS = {
    "agy": {"native", "cli"},
    "codex": {"native", "cli"},
    "gemini": {"api"},
}


def canonical_provider(provider):
    return "codex" if provider == "codex-builtin" else provider


def _locked_transport(plan, provider):
    transport = plan.get("image_transport")
    if transport:
        return transport
    original = plan.get("provider")
    if original == "codex-builtin":
        return "native"
    if provider == "codex":
        return "cli"
    if provider == "agy":
        return "native"
    if provider == "gemini":
        return "api"
    return None


def resolve_provider(requested_provider, requested_transport, plan):
    """Resolve a script invocation without allowing a locked deck to drift."""
    locked_provider = canonical_provider(plan.get("provider"))
    locked_transport = _locked_transport(plan, locked_provider)
    if requested_provider == "auto":
        if locked_provider:
            if locked_transport == "native":
                tool = (
                    "generate_image"
                    if locked_provider == "agy"
                    else "image_gen"
                )
                raise RuntimeError(
                    f"plan.json 已锁定 {locked_provider}/native；请由当前 "
                    f"agent 调用原生 {tool}，再用 --import-file 导入。"
                )
            return locked_provider, locked_transport
        return image_providers.detect_script_provider(), "api"

    if requested_provider == "both":
        if locked_provider:
            raise RuntimeError("设计已锁定，禁止用 both 混合后端")
        return "both", None

    provider = canonical_provider(requested_provider)
    transport = requested_transport
    if not transport and provider == locked_provider:
        transport = locked_transport
    if not transport:
        transport = "api" if provider == "gemini" else "cli"
    if provider not in PROVIDER_TRANSPORTS or \
            transport not in PROVIDER_TRANSPORTS[provider]:
        raise RuntimeError(f"{provider} 不支持 {transport} 传输")
    if locked_provider and (
        provider != locked_provider
        or (locked_transport and transport != locked_transport)
    ):
        raise RuntimeError(
            "显式后端与 plan.json 锁定不一致；先用 "
            "plan_tool.py provider 正式切换。"
        )
    return provider, transport


def validate_locked_model(provider, plan):
    """Ensure environment overrides cannot change a locked deck's model."""
    locked_model = plan.get("image_model")
    if not locked_model:
        return
    actual_model = {
        "agy": image_providers.DEFAULT_GEMINI_MODEL,
        "codex": image_providers.DEFAULT_CODEX_MODEL,
        "gemini": image_providers.gemini_model(),
    }[provider]
    if locked_model != actual_model:
        raise RuntimeError(
            f"plan.json 已锁定模型 {locked_model}，当前配置将使用 "
            f"{actual_model}；禁止静默切换模型"
        )


def _crop_box(width, height):
    target = 16 / 9
    if abs(width / height - target) <= 0.02:
        return None
    if width / height > target:
        new_width = int(height * target)
        left = (width - new_width) // 2
        return left, 0, left + new_width, height
    new_height = int(width / target)
    top = (height - new_height) // 2
    return 0, top, width, top + new_height


def import_native_artifact(source, out_path):
    """Normalize a host-native image artifact to a 16:9 RGB PNG."""
    from PIL import Image

    source = Path(source)
    out_path = Path(out_path)
    if not source.is_file():
        raise RuntimeError(f"原生生图产物不存在：{source}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        opened.load()
        image = opened.convert("RGB")
    original_size = image.size
    box = _crop_box(*image.size)
    if box:
        image = image.crop(box)
        print(
            f"[gen_image] 已居中裁切 {original_size[0]}x{original_size[1]} "
            f"-> {image.size[0]}x{image.size[1]} (16:9)"
        )
    image.save(out_path, format="PNG")
    return image.size


def postprocess(out_path):
    """Validate and crop a generated image to 16:9. Return width and height."""
    from PIL import Image

    path = Path(out_path)
    with Image.open(path) as opened:
        opened.load()
        image = opened.convert("RGB")
        original_format = opened.format
    width, height = image.size
    box = _crop_box(width, height)
    must_save_png = path.suffix.lower() == ".png" and original_format != "PNG"
    if box:
        image = image.crop(box)
        print(
            f"[gen_image] 已居中裁切 {width}x{height} -> "
            f"{image.size[0]}x{image.size[1]} (16:9)"
        )
        width, height = image.size
    if box or must_save_png:
        save_format = "PNG" if path.suffix.lower() == ".png" else None
        image.save(path, format=save_format)
    if width < 1280:
        print(f"[gen_image] 警告：宽度 {width} < 1280，建议重新生成更高分辨率")
    return width, height


def generate_with_retry(provider, prompt, out_path, refs, max_attempts):
    """Generate with one scripted provider and bounded retry."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            image_providers.generate(provider, prompt, out_path, refs)
            return True
        except urllib.error.HTTPError as error:
            last_error = error
            wait = min(2 ** attempt, 60) if error.code == 429 else 2
            print(
                f"[gen_image] {provider} 尝试{attempt}失败 HTTP "
                f"{error.code}，{wait}s后重试"
            )
            time.sleep(wait)
        except Exception as error:  # noqa: BLE001
            last_error = error
            print(
                f"[gen_image] {provider} 尝试{attempt}失败: "
                f"{str(error)[:200]}"
            )
            if attempt < max_attempts:
                time.sleep(2)
    print(
        f"[gen_image] {provider} {max_attempts} 次尝试均失败，"
        f"最后错误: {last_error}"
    )
    return False


def archive_existing(path):
    if os.path.exists(path):
        history = os.path.join(WS, "pages", "history")
        os.makedirs(history, exist_ok=True)
        shutil.move(
            path,
            os.path.join(
                history, f"{os.path.basename(path)}.{int(time.time())}"
            ),
        )


def finalize(plan, plan_path, page, out_path, update_state=True):
    width, height = postprocess(out_path)
    if update_state:
        page["status"] = "generated"
        with open(plan_path, "w", encoding="utf-8") as stream:
            json.dump(plan, stream, ensure_ascii=False, indent=2)
    state_note = (
        "状态已更新为 generated"
        if update_state
        else "等待协调器批量更新状态"
    )
    print(
        f"[gen_image] ✓ {out_path} ({width}x{height})，{state_note}。"
        "下一步：目检该图（constraints.md 检查清单）"
    )


def variant_path(page, provider):
    base = os.path.join(WS, page["image"])
    return (
        base[:-4] + f".{provider}.png"
        if base.endswith(".png")
        else base + f".{provider}.png"
    )


def _style_refs(plan, no_refs):
    if no_refs or not plan.get("style"):
        return []
    style_dir = os.path.join(
        REPO, "references", "design", "styles", plan["style"]
    )
    if not os.path.isdir(style_dir):
        return []
    return sorted(
        os.path.join(style_dir, name)
        for name in os.listdir(style_dir)
        if name.startswith("ref-")
    )[:2]


def _resolve_or_exit(provider, transport, plan):
    try:
        return resolve_provider(provider, transport, plan)
    except RuntimeError as error:
        sys.exit(f"[gen_image] {error}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True)
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "agy", "codex", "gemini", "both"],
    )
    parser.add_argument("--transport", choices=["native", "cli", "api"])
    parser.add_argument(
        "--import-file",
        help="导入当前 agent 原生生图工具产物并执行裁切/状态更新",
    )
    parser.add_argument(
        "--pick",
        choices=["codex", "gemini"],
        help="从 both 模式的两个变体中选定一个作为正式页面",
    )
    parser.add_argument("--no-refs", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument(
        "--no-state",
        action="store_true",
        help="并行 worker 不写 plan.json；由协调器统一更新",
    )
    args = parser.parse_args()

    plan_path = os.path.join(WS, "plan.json")
    with open(plan_path, encoding="utf-8") as stream:
        plan = json.load(stream)
    page = next(
        (item for item in plan["pages"] if item["id"] == args.page), None
    )
    if not page:
        sys.exit(f"[gen_image] 找不到页面 {args.page}")
    out_path = os.path.join(WS, page["image"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if args.pick:
        if plan.get("provider"):
            sys.exit("[gen_image] 设计已锁定，不能再从 both 变体切换")
        selected = variant_path(page, args.pick)
        if not os.path.exists(selected):
            sys.exit(
                f"[gen_image] 变体不存在: {selected}（先运行 --provider both）"
            )
        archive_existing(out_path)
        shutil.move(selected, out_path)
        other = variant_path(
            page, "gemini" if args.pick == "codex" else "codex"
        )
        if os.path.exists(other):
            archive_existing(other)
        print(
            f"[gen_image] 已选定 {args.pick} 版本作为 "
            f"{page['id']} 正式页面；请立即用 plan_tool.py provider 锁定后端"
        )
        finalize(plan, plan_path, page, out_path, not args.no_state)
        return

    provider, transport = _resolve_or_exit(
        args.provider, args.transport, plan
    )
    try:
        validate_locked_model(provider, plan)
    except RuntimeError as error:
        sys.exit(f"[gen_image] {error}")

    if args.import_file:
        if provider not in ("agy", "codex") or transport != "native":
            sys.exit(
                "[gen_image] --import-file 仅用于已锁定的 "
                "agy/native 或 codex/native"
            )
        source = Path(args.import_file).resolve()
        target = Path(out_path).resolve()
        if source != target:
            archive_existing(out_path)
        import_native_artifact(source, target)
        finalize(plan, plan_path, page, target, not args.no_state)
        return

    if transport == "native":
        tool = "generate_image" if provider == "agy" else "image_gen"
        sys.exit(
            f"[gen_image] {provider}/native 必须先调用原生 {tool}，"
            "再用 --import-file 导入产物"
        )

    prompt_path = os.path.join(WS, page["prompt_file"])
    if not os.path.exists(prompt_path):
        sys.exit(
            f"[gen_image] 提示词不存在，先运行 make_prompt.py "
            f"--page {args.page}"
        )
    with open(prompt_path, encoding="utf-8") as stream:
        prompt = stream.read()
    refs = _style_refs(plan, args.no_refs)
    ref_note = f"（垫图{len(refs)}张）" if refs else ""

    if provider == "both":
        results = {}
        for candidate in ("codex", "gemini"):
            if not image_providers.provider_available(candidate):
                print(f"[gen_image] 跳过 {candidate}（不可用）")
                continue
            candidate_path = variant_path(page, candidate)
            archive_existing(candidate_path)
            print(
                f"[gen_image] {args.page} via {candidate}{ref_note} ..."
            )
            if generate_with_retry(
                candidate,
                prompt,
                candidate_path,
                refs,
                args.max_attempts,
            ):
                postprocess(candidate_path)
                results[candidate] = candidate_path
        if not results:
            sys.exit("[gen_image] both 模式：两个后端均失败")
        print("[gen_image] 对比版本已生成:")
        for candidate, candidate_path in results.items():
            print(f"  {candidate:6s} -> {candidate_path}")
        print(
            f"[gen_image] 目检后选定: gen_image.py --page {args.page} "
            "--pick codex|gemini，然后锁定后端"
        )
        return

    if not image_providers.provider_available(provider):
        sys.exit(f"[gen_image] {provider}/{transport} 当前不可用")
    archive_existing(out_path)
    print(
        f"[gen_image] {args.page} via {provider}/{transport}{ref_note} ..."
    )
    if not generate_with_retry(
        provider, prompt, out_path, refs, args.max_attempts
    ):
        sys.exit(1)
    finalize(plan, plan_path, page, out_path, not args.no_state)


if __name__ == "__main__":
    main()
