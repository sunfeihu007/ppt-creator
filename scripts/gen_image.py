#!/usr/bin/env python3
"""生图执行器：双后端（Gemini API / 本地 Codex CLI→gpt-image-2），带重试与16:9裁切。

后端说明:
  gemini : 直连 Google Gemini API。需要环境变量 GEMINI_API_KEY 或 GOOGLE_API_KEY。
           模型名取 GEMINI_IMAGE_MODEL（默认 gemini-3.1-flash-image-preview）。
           key 通过 x-goog-api-key header 发送，不拼在 URL 里。
  codex  : 调用本地 codex CLI（`codex exec`），由 Codex 内置 image_gen 工具（gpt-image-2）
           生图，走 ChatGPT 订阅鉴权 —— 不需要 OpenAI API key。
           可用 PPTC_CODEX_BIN 指定二进制（默认 codex）。
  auto   : 有 Gemini key → gemini；否则找得到 codex 命令 → codex；否则报错。

注意：若你本身就在 Codex 环境中运行本 skill，不要用本脚本，
直接用内置 image_gen 工具按 prompts/PXX.txt 生图（见 SKILL.md）。

用法:
  gen_image.py --page P01 [--provider auto|gemini|codex] [--no-refs] [--max-attempts 8]
成功后自动: 校验图片 → 裁切为16:9 → 更新 plan.json 页面状态为 generated。
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

WS = os.environ.get("PPTC_WORKSPACE", "./ppt_workspace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEMINI_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")
CODEX_BIN = os.environ.get("PPTC_CODEX_BIN", "codex")


def gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def detect_provider():
    if gemini_key():
        return "gemini"
    if shutil.which(CODEX_BIN):
        return "codex"
    sys.exit("[gen_image] 无可用生图后端：请 export GEMINI_API_KEY=...，"
             "或安装 codex CLI（https://developers.openai.com/codex/cli）。"
             "不要把 key 粘贴到对话里。")


def gen_gemini(prompt, out_path, refs, timeout=300):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent")
    parts = [{"text": prompt}]
    for r in refs:
        with open(r, "rb") as f:
            parts.append({"inlineData": {
                "mimeType": "image/jpeg",
                "data": base64.b64encode(f.read()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"imageSize": "2K",
                                                 "aspectRatio": "16:9"}}}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": gemini_key()},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode())
    if "error" in result:
        raise RuntimeError(result["error"].get("message", str(result["error"])))
    for cand in result.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or {}).get("data")
            if data:
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(data))
                return
    fr = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
    raise RuntimeError(f"No image returned (finishReason={fr})")


def gen_codex(prompt, out_path, refs, timeout=600):
    """通过本地 codex CLI 的内置 image_gen 工具（gpt-image-2）生图。"""
    out_abs = os.path.abspath(out_path)
    instruction = (
        "Use your built-in image generation tool (image_gen / $imagegen, gpt-image-2) to "
        "create ONE image: a 16:9 presentation slide, 1920x1080 pixels. "
        f"Save the final image EXACTLY to this path: {out_abs} . "
        "Do not create or modify any other files. Do not ask questions.\n")
    if refs:
        instruction += ("Style reference images (follow their layout and texture, IGNORE "
                        "their colors): " + ", ".join(os.path.abspath(r) for r in refs) + "\n")
    instruction += "\nImage prompt:\n" + prompt
    cmd = [CODEX_BIN, "exec", "--skip-git-repo-check", instruction]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        sys.exit(f"[gen_image] 找不到 codex 命令（{CODEX_BIN}）")
    if res.returncode != 0 and "--skip-git-repo-check" in (res.stderr or ""):
        # 旧版本 codex 无此 flag，去掉重试
        res = subprocess.run([CODEX_BIN, "exec", instruction],
                             capture_output=True, text=True, timeout=timeout)
    if not os.path.exists(out_abs):
        raise RuntimeError(
            f"codex exec 未产出图片（returncode={res.returncode}）。stderr尾部: "
            f"{(res.stderr or '')[-500:]}")


def postprocess(out_path):
    """校验+裁切16:9。返回 (width, height)。"""
    from PIL import Image
    im = Image.open(out_path)
    im.load()
    w, h = im.size
    target = 16 / 9
    if abs(w / h - target) > 0.02:  # 非16:9 → 居中裁切
        if w / h > target:
            nw = int(h * target)
            box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
        else:
            nh = int(w / target)
            box = (0, (h - nh) // 2, w, (h - nh) // 2 + nh)
        im = im.convert("RGB").crop(box)
        im.save(out_path)
        print(f"[gen_image] 已居中裁切 {w}x{h} -> {im.size[0]}x{im.size[1]} (16:9)")
        w, h = im.size
    if w < 1280:
        print(f"[gen_image] 警告：宽度 {w} < 1280，建议重新生成更高分辨率")
    return w, h


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--page", required=True)
    ap.add_argument("--provider", default="auto",
                    choices=["auto", "gemini", "codex"])
    ap.add_argument("--no-refs", action="store_true")
    ap.add_argument("--max-attempts", type=int, default=8)
    args = ap.parse_args()

    plan_path = os.path.join(WS, "plan.json")
    plan = json.load(open(plan_path, encoding="utf-8"))
    page = next((p for p in plan["pages"] if p["id"] == args.page), None)
    if not page:
        sys.exit(f"[gen_image] 找不到页面 {args.page}")
    prompt_path = os.path.join(WS, page["prompt_file"])
    if not os.path.exists(prompt_path):
        sys.exit(f"[gen_image] 提示词不存在，先运行 make_prompt.py --page {args.page}")
    prompt = open(prompt_path, encoding="utf-8").read()

    provider = args.provider
    if provider == "auto":
        provider = plan.get("provider") if plan.get("provider") in ("gemini", "codex") \
            else detect_provider()
    refs = []
    if not args.no_refs and plan.get("style"):
        sdir = os.path.join(REPO, "references", "design", "styles", plan["style"])
        if os.path.isdir(sdir):
            refs = sorted(os.path.join(sdir, f) for f in os.listdir(sdir)
                          if f.startswith("ref-"))[:2]

    out_path = os.path.join(WS, page["image"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if os.path.exists(out_path):  # 保留历史版本
        hist = os.path.join(WS, "pages", "history")
        os.makedirs(hist, exist_ok=True)
        shutil.move(out_path, os.path.join(
            hist, f"{page['id']}_{int(time.time())}.png"))

    gen = gen_gemini if provider == "gemini" else gen_codex
    print(f"[gen_image] {args.page} via {provider}"
          f"{'（垫图' + str(len(refs)) + '张）' if refs else ''} ...")
    last_err = None
    for attempt in range(1, args.max_attempts + 1):
        try:
            gen(prompt, out_path, refs)
            w, h = postprocess(out_path)
            page["status"] = "generated"
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            print(f"[gen_image] ✓ {out_path} ({w}x{h})，状态已更新为 generated。"
                  f"下一步：目检该图（constraints.md 检查清单）")
            return
        except urllib.error.HTTPError as e:
            last_err = e
            wait = min(2 ** attempt, 60) if e.code == 429 else 2
            print(f"[gen_image] 尝试{attempt}失败 HTTP {e.code}，{wait}s后重试")
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[gen_image] 尝试{attempt}失败: {str(e)[:200]}")
            time.sleep(2)
    sys.exit(f"[gen_image] {args.max_attempts} 次尝试均失败，最后错误: {last_err}")


if __name__ == "__main__":
    main()
