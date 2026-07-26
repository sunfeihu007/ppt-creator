#!/usr/bin/env python3
"""Generate three neutral 16:9 previews for a registered semantic palette."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, ImageColor, ImageDraw


REPO = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO / "references" / "design"
WIDTH = 1600
HEIGHT = 900


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_colors(path):
    text = Path(path).read_text(encoding="utf-8")
    colors = {}
    for line in text.splitlines():
        match = re.match(
            r"\|\s*`\{([A-Z][A-Z0-9_]*)\}`\s*\|\s*`([^`]+)`",
            line,
        )
        if not match:
            continue
        hexes = re.findall(r"#[0-9A-Fa-f]{6}", match.group(2))
        if hexes:
            colors[match.group(1)] = hexes[0].upper()
    required = {
        "BACKGROUND",
        "SURFACE",
        "STRUCTURE",
        "FOCUS",
        "TEXT_PRIMARY",
        "TEXT_SECONDARY",
        "BORDER",
    }
    missing = required - set(colors)
    if missing:
        raise ValueError(f"配色缺少预览所需 Token：{sorted(missing)}")
    return colors


def rgb(colors, role):
    return ImageColor.getrgb(colors[role])


def rgba(colors, role, alpha):
    return (*rgb(colors, role), alpha)


def canvas(colors):
    return Image.new("RGBA", (WIDTH, HEIGHT), rgba(colors, "BACKGROUND", 255))


def grid(draw, colors, step=80):
    line = rgba(colors, "BORDER", 90)
    for x in range(0, WIDTH, step):
        draw.line((x, 0, x, HEIGHT), fill=line, width=1)
    for y in range(0, HEIGHT, step):
        draw.line((0, y, WIDTH, y), fill=line, width=1)


def bars(draw, colors, x, y, widths, gap=34):
    for index, width in enumerate(widths):
        fill = (
            rgba(colors, "TEXT_PRIMARY", 210)
            if index == 0
            else rgba(colors, "TEXT_SECONDARY", 135)
        )
        height = 18 if index == 0 else 11
        draw.rounded_rectangle(
            (x, y, x + width, y + height),
            radius=height // 2,
            fill=fill,
        )
        y += gap


def glass_panel(base, box, colors, radius=34, alpha=176):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=rgba(colors, "SURFACE", alpha),
        outline=rgba(colors, "SURFACE", 235),
        width=3,
    )
    x1, y1, x2, _y2 = box
    draw.line(
        (x1 + radius, y1 + 3, x2 - radius, y1 + 3),
        fill=rgba(colors, "SURFACE", 255),
        width=4,
    )
    base.alpha_composite(layer)


def draw_cover(colors):
    image = canvas(colors)
    draw = ImageDraw.Draw(image)
    grid(draw, colors, 100)
    draw.rectangle((0, 0, 32, HEIGHT), fill=rgba(colors, "FOCUS", 255))
    draw.ellipse((1040, 110, 1540, 610), fill=rgba(colors, "FOCUS", 40))
    draw.ellipse((1180, 250, 1450, 520), fill=rgba(colors, "FOCUS", 210))
    glass_panel(image, (790, 170, 1400, 750), colors, radius=42, alpha=168)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (880, 275, 1210, 515),
        radius=28,
        fill=rgba(colors, "SURFACE", 235),
        outline=rgba(colors, "BORDER", 255),
        width=3,
    )
    draw.rounded_rectangle(
        (1090, 390, 1320, 625),
        radius=28,
        fill=rgba(colors, "STRUCTURE", 232),
    )
    bars(draw, colors, 130, 225, [500, 390, 310], gap=52)
    draw.rectangle((130, 545, 520, 558), fill=rgba(colors, "FOCUS", 255))
    return image


def draw_architecture(colors):
    image = canvas(colors)
    draw = ImageDraw.Draw(image)
    grid(draw, colors)
    bars(draw, colors, 95, 70, [420, 270], gap=42)
    rows = [
        (230, 355, 580, 485),
        (625, 355, 975, 485),
        (1020, 355, 1370, 485),
    ]
    for index, box in enumerate(rows):
        draw.rounded_rectangle(
            box,
            radius=20,
            fill=rgba(colors, "SURFACE", 255),
            outline=rgba(colors, "BORDER", 255),
            width=3,
        )
        x1, y1, x2, _y2 = box
        draw.rectangle(
            (x1 + 34, y1 + 36, x1 + 78, y1 + 80),
            fill=rgba(colors, "FOCUS" if index == 1 else "STRUCTURE", 255),
        )
        bars(draw, colors, x1 + 105, y1 + 40, [180, 135], gap=34)
        if index < 2:
            draw.line(
                (x2, 420, rows[index + 1][0], 420),
                fill=rgba(colors, "STRUCTURE", 205),
                width=5,
            )
    draw.rounded_rectangle(
        (340, 620, 1260, 750),
        radius=18,
        fill=rgba(colors, "STRUCTURE", 245),
    )
    for x in (430, 700, 970):
        draw.ellipse((x, 655, x + 58, 713), fill=rgba(colors, "SURFACE", 235))
    glass_panel(image, (545, 280, 1055, 555), colors, radius=30, alpha=112)
    return image


def draw_detail(colors):
    image = canvas(colors)
    draw = ImageDraw.Draw(image)
    bars(draw, colors, 95, 70, [360, 245], gap=42)
    draw.rounded_rectangle(
        (95, 215, 1090, 760),
        radius=26,
        fill=rgba(colors, "SURFACE", 255),
        outline=rgba(colors, "BORDER", 255),
        width=3,
    )
    draw.rectangle((135, 255, 1050, 550), fill=rgba(colors, "BORDER", 125))
    draw.polygon(
        [(170, 520), (420, 330), (690, 520)],
        fill=rgba(colors, "STRUCTURE", 155),
    )
    draw.ellipse((760, 315, 925, 480), fill=rgba(colors, "FOCUS", 180))
    draw.line((350, 620, 960, 620), fill=rgba(colors, "STRUCTURE", 195), width=5)
    for x in (350, 550, 760, 960):
        draw.ellipse((x - 14, 606, x + 14, 634), fill=rgba(colors, "FOCUS", 255))
    draw.rounded_rectangle(
        (1140, 215, 1505, 760),
        radius=26,
        fill=rgba(colors, "STRUCTURE", 247),
    )
    bars(draw, colors, 1195, 285, [230, 175, 215, 150], gap=58)
    glass_panel(image, (830, 500, 1195, 700), colors, radius=28, alpha=150)
    return image


DRAWERS = (
    ("cover", draw_cover),
    ("architecture", draw_architecture),
    ("detail", draw_detail),
)


def generate(palette, output, design=DEFAULT_DESIGN):
    palette_path = Path(design) / "palettes" / f"{palette}.md"
    if not palette_path.is_file():
        raise ValueError(f"未登记配色：{palette}")
    colors = parse_colors(palette_path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    assets = []
    for role, drawer in DRAWERS:
        path = output / f"{role}.jpg"
        drawer(colors).convert("RGB").save(
            path,
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
            progressive=False,
        )
        assets.append(
            {
                "role": role,
                "file": path.name,
                "width": WIDTH,
                "height": HEIGHT,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "version": 1,
        "palette": palette,
        "rules": {
            "text_free": True,
            "brand_free": True,
            "data_free": True,
        },
        "colors": colors,
        "assets": assets,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--design", default=str(DEFAULT_DESIGN))
    args = parser.parse_args()
    try:
        manifest = generate(args.palette, args.output, args.design)
    except ValueError as exc:
        parser.error(str(exc))
    print(
        f"[generate_palette_preview] generated {len(manifest['assets'])} "
        f"neutral previews for {manifest['palette']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
