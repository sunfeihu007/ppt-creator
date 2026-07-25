#!/usr/bin/env python3
"""Scripted image-provider adapters used by gen_image.py.

Host-native AGY ``generate_image`` and Codex ``image_gen`` calls are made by
the agent itself. This module supports Gemini API plus explicit AGY/Codex CLI
compatibility bridges.
"""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import uuid


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-image"
DEFAULT_CODEX_MODEL = "gpt-image-2"
DEFAULT_AGY_BRAIN_DIR = "~/.gemini/antigravity-cli/brain"


def agy_bin():
    return os.environ.get("PPTC_AGY_BIN", "agy")


def codex_bin():
    return os.environ.get("PPTC_CODEX_BIN", "codex")


def gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def gemini_model():
    return os.environ.get("GEMINI_IMAGE_MODEL", DEFAULT_GEMINI_MODEL)


def detect_script_provider():
    """Return the default backend for non-native clients."""
    if gemini_key():
        return "gemini"
    raise RuntimeError(
        "其他客户端默认通过 Gemini API 生图；请设置 GEMINI_API_KEY 或 "
        "GOOGLE_API_KEY。不要把 key 粘贴到对话中。"
    )


def provider_available(name):
    if name == "gemini":
        return bool(gemini_key())
    if name == "agy":
        return bool(shutil.which(agy_bin()))
    if name == "codex":
        return bool(shutil.which(codex_bin()))
    return False


def _reference_mime_type(path):
    suffix = Path(path).suffix.lower()
    return "image/png" if suffix == ".png" else "image/jpeg"


def generate_gemini(prompt, out_path, refs, timeout=300):
    key = gemini_key()
    if not key:
        raise RuntimeError(
            "Gemini API 未配置：请设置 GEMINI_API_KEY 或 GOOGLE_API_KEY。"
        )
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{gemini_model()}:generateContent"
    )
    parts = [{"text": prompt}]
    for ref in refs:
        with open(ref, "rb") as stream:
            parts.append({
                "inlineData": {
                    "mimeType": _reference_mime_type(ref),
                    "data": base64.b64encode(stream.read()).decode(),
                }
            })
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"imageSize": "2K", "aspectRatio": "16:9"},
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if "error" in result:
        error = result["error"]
        raise RuntimeError(error.get("message", str(error)))
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or {}).get("data")
            if data:
                Path(out_path).write_bytes(base64.b64decode(data))
                return
    finish_reason = (
        result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
    )
    raise RuntimeError(f"No image returned (finishReason={finish_reason})")


def generate_codex(prompt, out_path, refs, timeout=600):
    out_abs = str(Path(out_path).resolve())
    instruction = (
        "Use your built-in image generation tool (image_gen / $imagegen, "
        "gpt-image-2) to create ONE image: a 16:9 presentation slide, "
        "1920x1080 pixels. Save the final image EXACTLY to this path: "
        f"{out_abs}. Do not create or modify any other files. "
        "Do not ask questions.\n"
    )
    if refs:
        instruction += (
            "Style reference images (follow layout and texture, ignore their "
            "colors): "
            + ", ".join(str(Path(ref).resolve()) for ref in refs)
            + "\n"
        )
    instruction += "\nImage prompt:\n" + prompt
    command = [
        codex_bin(),
        "exec",
        "--skip-git-repo-check",
        instruction,
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError as error:
        raise RuntimeError(f"找不到 codex 命令（{codex_bin()}）") from error
    if (
        result.returncode != 0
        and "--skip-git-repo-check" in (result.stderr or "")
    ):
        result = subprocess.run(
            [codex_bin(), "exec", instruction],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    if not Path(out_abs).exists():
        raise RuntimeError(
            "codex exec 未产出图片"
            f"（returncode={result.returncode}）。stderr尾部: "
            f"{(result.stderr or '')[-500:]}"
        )


def preflight_agy(timeout=60):
    """Verify that AGY print mode returns a usable response."""
    marker = "PPTC_AGY_PREFLIGHT_OK"
    command = [
        agy_bin(),
        "--print-timeout",
        "1m",
        "-p",
        f"Reply exactly {marker}",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError as error:
        raise RuntimeError(f"找不到 agy 命令（{agy_bin()}）") from error
    if result.returncode != 0 or marker not in (result.stdout or ""):
        raise RuntimeError(
            "AGY CLI preflight 失败：当前 agy -p 未返回可用响应；"
            "请在 AGY 内直接使用原生 generate_image，或修复 AGY CLI 会话。"
        )


def find_agy_artifact(root, image_name, started_at):
    root = Path(root).expanduser()
    if not root.is_dir():
        raise RuntimeError(f"AGY 图片目录不存在：{root}")
    candidates = []
    for suffix in ("jpg", "jpeg", "png", "webp"):
        for path in root.rglob(f"{image_name}*.{suffix}"):
            if path.stat().st_mtime >= started_at:
                candidates.append(path)
    if not candidates:
        raise RuntimeError(
            f"AGY CLI 未找到本次图片：ImageName={image_name}，目录={root}"
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def generate_agy(prompt, out_path, refs, timeout=600):
    """Experimental AGY print-mode bridge. Never selected automatically."""
    preflight_agy(timeout=min(timeout, 60))
    image_name = f"{Path(out_path).stem}-{uuid.uuid4().hex[:10]}"
    brain_dir = Path(
        os.environ.get("PPTC_AGY_BRAIN_DIR", DEFAULT_AGY_BRAIN_DIR)
    ).expanduser()
    started_at = time.time()
    reference_note = ""
    if refs:
        reference_note = (
            "\nAGY generate_image 当前没有独立参考图参数。请仅把以下路径作为"
            "版式和质感语义参考，颜色仍严格服从提示词："
            + ", ".join(str(Path(ref).resolve()) for ref in refs)
        )
    instruction = (
        "Call the native generate_image tool exactly once. "
        f"Set ImageName to {image_name}; set AspectRatio to 16:9. "
        "Return no prose until the image is saved.\n\n"
        f"Image prompt:\n{prompt}{reference_note}"
    )
    result = subprocess.run(
        [agy_bin(), "--print-timeout", "10m", "-p", instruction],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"agy -p 生图失败（returncode={result.returncode}）："
            f"{(result.stderr or '')[-500:]}"
        )
    artifact = find_agy_artifact(brain_dir, image_name, started_at)
    shutil.copy2(artifact, out_path)


def generate(provider, prompt, out_path, refs, timeout=None):
    adapters = {
        "agy": (generate_agy, 600),
        "codex": (generate_codex, 600),
        "gemini": (generate_gemini, 300),
    }
    if provider not in adapters:
        raise ValueError(f"unknown image provider: {provider}")
    adapter, default_timeout = adapters[provider]
    adapter(prompt, out_path, refs, timeout=timeout or default_timeout)
