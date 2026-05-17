#!/usr/bin/env python3
"""
PPT页面生成示例脚本
使用Gemini NanoBanana 2 (gemini-3.1-flash-image-preview)

使用方法:
1. 设置环境变量: export GOOGLE_API_KEY='your_api_key_here'
2. 运行脚本: python generate_ppt_example.py
"""

import json
import base64
import os
import time
import urllib.request
from urllib.error import HTTPError

# 从环境变量获取API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    print("错误: 请设置环境变量 GOOGLE_API_KEY")
    print("示例: export GOOGLE_API_KEY='your_api_key_here'")
    exit(1)

MODEL = "gemini-3.1-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
OUTPUT_DIR = "./ppt_pages"

# 示例页面配置
PAGES = [
    {
        "name": "P01_封面页",
        "prompt": """Create a premium professional PPT cover slide, 16:9 ratio, light gray-white gradient background.

Title: 新一代知识管理平台
Subtitle: AI原生时代的知识治理与智能赋能

Style: 3D glass morphism, China Unicom red (#E60012) accent, professional business style.
""",
        "image_size": "2K"
    }
]

def gemini_generate(prompt, image_size="2K", timeout_sec=300):
    """使用Gemini API生成图片"""
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "imageSize": image_size,
                "aspectRatio": "16:9"
            }
        }
    }
    
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    
    if "error" in result:
        raise RuntimeError(result["error"].get("message", str(result["error"])))
    
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline_data = part.get("inlineData")
            if inline_data and inline_data.get("data"):
                return base64.b64decode(inline_data["data"])
    
    finish_reason = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
    raise RuntimeError(f"No image returned (finishReason={finish_reason})")

def generate_page(page_config, max_attempts=8):
    """生成单个页面，带重试机制"""
    name = page_config["name"]
    prompt = page_config["prompt"]
    image_size = page_config.get("image_size", "2K")
    output_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    
    print(f"\n生成页面: {name}")
    
    for attempt in range(1, max_attempts + 1):
        print(f"  尝试 {attempt}/{max_attempts}...")
        
        try:
            image_bytes = gemini_generate(prompt=prompt, image_size=image_size)
            
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"  ✓ 成功! 已保存: {output_path}")
            return True
            
        except HTTPError as e:
            print(f"  ✗ HTTP错误: {e.code} - {e.reason}")
            if e.code == 429:
                wait_time = min(2 ** attempt, 60)
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                time.sleep(2)
                
        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")
            time.sleep(2)
    
    return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("PPT页面生成示例")
    print(f"模型: {MODEL}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    success_count = 0
    for page in PAGES:
        if generate_page(page):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"生成完成! 成功: {success_count}/{len(PAGES)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
