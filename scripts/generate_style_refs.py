#!/usr/bin/env python3
"""Generate deterministic, text-free, brand-free visual references for PPT styles."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw


REPO = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO / "references" / "design"
WIDTH = 1600
HEIGHT = 900

PAPER = (246, 247, 247, 255)
WHITE = (253, 253, 252, 255)
SURFACE = (229, 233, 235, 255)
MID = (132, 144, 151, 255)
INK = (42, 50, 56, 255)
ACCENT = (72, 96, 116, 255)
LIGHT_ACCENT = (174, 190, 199, 255)
DARK = (17, 27, 35, 255)
DARK_SURFACE = (28, 42, 52, 255)
DARK_LINE = (91, 145, 153, 255)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def header(draw, dark=False):
    ink = (225, 232, 234, 255) if dark else INK
    muted = (112, 137, 145, 255) if dark else MID
    draw.rectangle((88, 76, 112, 100), fill=ACCENT if not dark else DARK_LINE)
    draw.rectangle((132, 76, 468, 96), fill=ink)
    draw.rectangle((132, 112, 342, 123), fill=muted)
    draw.line((88, 148, 1512, 148), fill=muted, width=2)


def clipped_panel(draw, box, fill=WHITE, outline=SURFACE, clip=36, width=3):
    x1, y1, x2, y2 = box
    points = [
        (x1, y1),
        (x2 - clip, y1),
        (x2, y1 + clip),
        (x2, y2),
        (x1, y2),
    ]
    draw.polygon(points, fill=fill, outline=outline)
    draw.line((x2 - clip, y1, x2 - clip, y1 + clip, x2, y1 + clip),
              fill=outline, width=width)


def bars(draw, x, y, widths, color=INK, height=16, gap=20):
    for index, width in enumerate(widths):
        top = y + index * (height + gap)
        draw.rectangle((x, top, x + width, top + height), fill=color)


def isometric_block(draw, x, y, w, h, depth, top=LIGHT_ACCENT):
    left = (204, 212, 216, 255)
    right = (151, 164, 171, 255)
    front = (231, 234, 235, 255)
    draw.polygon(
        [(x, y), (x + w, y), (x + w + depth, y - depth),
         (x + depth, y - depth)],
        fill=top,
        outline=ACCENT,
    )
    draw.polygon(
        [(x, y), (x + depth, y - depth), (x + depth, y + h - depth),
         (x, y + h)],
        fill=left,
        outline=ACCENT,
    )
    draw.polygon(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
        fill=front,
        outline=ACCENT,
    )
    draw.polygon(
        [(x + w, y), (x + w + depth, y - depth),
         (x + w + depth, y + h - depth), (x + w, y + h)],
        fill=right,
        outline=ACCENT,
    )


def draw_card_modern(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    header(draw)
    if variant == 0:
        bars(draw, 110, 258, [460, 380, 260], height=28, gap=26)
        clipped_panel(draw, (870, 235, 1450, 720), fill=WHITE, outline=ACCENT)
        draw.line((970, 600, 1120, 420, 1310, 520), fill=INK, width=8)
        draw.ellipse((1090, 385, 1160, 455), outline=ACCENT, width=7)
        draw.rectangle((1250, 492, 1340, 582), outline=ACCENT, width=7)
        draw.rectangle((868, 235, 900, 720), fill=ACCENT)
    elif variant == 1:
        clipped_panel(draw, (90, 220, 525, 760), fill=SURFACE, outline=LIGHT_ACCENT)
        draw.rectangle((132, 274, 300, 316), fill=ACCENT)
        bars(draw, 132, 376, [272, 238, 198], color=MID, height=14, gap=24)
        rows = [(590, 225, 1450, 330), (650, 360, 1450, 475),
                (590, 510, 1450, 620), (720, 655, 1450, 760)]
        for index, box in enumerate(rows):
            clipped_panel(draw, box, outline=LIGHT_ACCENT, clip=24)
            draw.rectangle(
                (box[0] + 32, box[1] + 30, box[0] + 48, box[3] - 30),
                fill=ACCENT if index == 1 else MID,
            )
            bars(draw, box[0] + 80, box[1] + 32, [220, 330],
                 color=INK if index == 1 else MID, height=12, gap=14)
    else:
        clipped_panel(draw, (90, 225, 1035, 760), outline=LIGHT_ACCENT)
        draw.rectangle((90, 225, 122, 760), fill=ACCENT)
        draw.rectangle((180, 310, 900, 610), fill=SURFACE)
        draw.line((210, 560, 400, 415, 620, 505, 840, 350),
                  fill=ACCENT, width=7)
        draw.rectangle((1090, 225, 1450, 760), outline=LIGHT_ACCENT, width=3)
        bars(draw, 1135, 290, [230, 270, 180, 250], color=MID,
             height=13, gap=40)
    return image


def draw_flat_editorial(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    if variant == 0:
        draw.polygon([(0, 0), (920, 0), (760, 900), (0, 900)], fill=INK)
        draw.rectangle((110, 138, 142, 196), fill=LIGHT_ACCENT)
        bars(draw, 110, 270, [510, 470, 360], color=WHITE, height=35, gap=28)
        draw.line((110, 540, 650, 540), fill=LIGHT_ACCENT, width=4)
        draw.rectangle((1045, 165, 1450, 700), fill=SURFACE)
        draw.line((1045, 700, 1450, 165), fill=LIGHT_ACCENT, width=5)
    elif variant == 1:
        header(draw)
        draw.rectangle((90, 235, 530, 750), fill=INK)
        draw.rectangle((130, 285, 400, 330), fill=WHITE)
        bars(draw, 130, 420, [260, 330, 220], color=LIGHT_ACCENT,
             height=12, gap=26)
        y_positions = [240, 365, 510, 665]
        widths = [690, 580, 760, 520]
        for index, (top, width) in enumerate(zip(y_positions, widths)):
            draw.line((620, top, 1470, top), fill=SURFACE, width=3)
            draw.rectangle((620, top + 26, 650, top + 56),
                           fill=ACCENT if index == 2 else MID)
            draw.rectangle((690, top + 30, 690 + width, top + 48), fill=INK)
    else:
        header(draw)
        draw.rectangle((90, 225, 1050, 760), fill=SURFACE)
        for offset in range(0, 960, 120):
            draw.line((90 + offset, 225, 90 + offset, 760),
                      fill=(215, 220, 222, 255), width=2)
        draw.polygon([(210, 650), (430, 360), (620, 540), (890, 300)],
                     fill=None, outline=ACCENT)
        draw.line((210, 650, 430, 360, 620, 540, 890, 300),
                  fill=ACCENT, width=8)
        draw.line((1100, 225, 1100, 760), fill=INK, width=4)
        bars(draw, 1150, 260, [250, 185, 285, 210], color=MID,
             height=14, gap=54)
    return image


def glass_panel(image, box, radius=34, alpha=105):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=(255, 255, 255, alpha),
        outline=(255, 255, 255, 205),
        width=4,
    )
    x1, y1, x2, _y2 = box
    draw.line((x1 + radius, y1 + 10, x2 - radius, y1 + 10),
              fill=(255, 255, 255, 220), width=4)
    image.alpha_composite(overlay)


def draw_glass(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), (224, 232, 236, 255))
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((930, 80, 1550, 700), fill=(136, 165, 178, 80))
    gd.ellipse((420, 420, 1050, 1020), fill=(190, 202, 209, 105))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image)
    header(draw)
    if variant == 0:
        bars(draw, 100, 260, [450, 390, 260], height=28, gap=24)
        glass_panel(image, (875, 230, 1440, 710), radius=42)
        draw = ImageDraw.Draw(image)
        isometric_block(draw, 1020, 535, 230, 115, 75)
        isometric_block(draw, 1090, 420, 190, 90, 62,
                        top=(208, 222, 227, 255))
        isometric_block(draw, 1140, 325, 135, 65, 48,
                        top=(181, 201, 208, 255))
    elif variant == 1:
        glass_panel(image, (320, 205, 1280, 760), radius=44)
        draw = ImageDraw.Draw(image)
        for index, y in enumerate((590, 465, 350)):
            isometric_block(
                draw, 540 + index * 80, y, 420 - index * 80, 75, 62,
                top=(196 - index * 12, 213 - index * 6, 220, 255),
            )
        for x in (230, 1370):
            draw.rounded_rectangle(
                (x - 90, 360, x + 90, 530),
                radius=28,
                fill=SURFACE,
                outline=LIGHT_ACCENT,
                width=4,
            )
        draw.line((320, 445, 220, 445), fill=ACCENT, width=5)
        draw.line((1280, 445, 1460, 445), fill=ACCENT, width=5)
    else:
        glass_panel(image, (90, 220, 980, 760), radius=40)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            (1040, 220, 1465, 510),
            radius=32,
            fill=SURFACE,
            outline=LIGHT_ACCENT,
            width=4,
        )
        draw.rounded_rectangle(
            (1120, 555, 1465, 760),
            radius=32,
            fill=SURFACE,
            outline=LIGHT_ACCENT,
            width=4,
        )
        draw.ellipse((300, 340, 665, 705), outline=ACCENT, width=8)
        draw.line((480, 340, 760, 265), fill=ACCENT, width=6)
        bars(draw, 1090, 285, [230, 180], color=MID, height=13, gap=22)
        bars(draw, 1170, 610, [190, 235], color=MID, height=13, gap=22)
    return image


def hud_grid(draw):
    for x in range(80, WIDTH, 120):
        draw.line((x, 160, x, 840), fill=(30, 58, 66, 255), width=1)
    for y in range(180, HEIGHT, 90):
        draw.line((60, y, 1540, y), fill=(30, 58, 66, 255), width=1)


def brackets(draw, box):
    x1, y1, x2, y2 = box
    size = 48
    for x, sx in ((x1, 1), (x2, -1)):
        for y, sy in ((y1, 1), (y2, -1)):
            draw.line((x, y, x + sx * size, y), fill=DARK_LINE, width=5)
            draw.line((x, y, x, y + sy * size), fill=DARK_LINE, width=5)


def draw_hud(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), DARK)
    draw = ImageDraw.Draw(image)
    hud_grid(draw)
    header(draw, dark=True)
    brackets(draw, (82, 195, 1518, 820))
    if variant == 0:
        bars(draw, 105, 275, [430, 335, 245],
             color=(222, 232, 233, 255), height=24, gap=24)
        draw.polygon(
            [(1020, 280), (1320, 350), (1370, 610), (1120, 730),
             (900, 610), (900, 390)],
            outline=DARK_LINE,
        )
        for offset in (0, 45, 90):
            draw.line((930 + offset, 600, 1100 + offset, 340),
                      fill=DARK_LINE, width=4)
    elif variant == 1:
        boxes = [(170, 300, 430, 470), (650, 240, 1030, 510),
                 (1180, 390, 1430, 565), (620, 620, 1030, 760)]
        for index, box in enumerate(boxes):
            draw.rectangle(box, outline=DARK_LINE, width=4)
            bars(draw, box[0] + 30, box[1] + 36,
                 [int((box[2] - box[0]) * 0.5),
                  int((box[2] - box[0]) * 0.35)],
                 color=(87, 121, 129, 255), height=9, gap=18)
        draw.line((430, 385, 650, 385), fill=DARK_LINE, width=4)
        draw.line((1030, 375, 1180, 475), fill=DARK_LINE, width=4)
        draw.line((840, 510, 840, 620), fill=DARK_LINE, width=4)
    else:
        draw.rectangle((130, 235, 1030, 760), outline=DARK_LINE, width=4)
        draw.polygon([(340, 650), (520, 360), (760, 420), (880, 650)],
                     outline=DARK_LINE)
        draw.line((1080, 250, 1080, 760), fill=DARK_LINE, width=3)
        for y, width in ((285, 260), (390, 320), (515, 210), (650, 300)):
            draw.line((1135, y, 1135 + width, y), fill=DARK_LINE, width=6)
            draw.line((1135, y + 22, 1135 + width * 0.65, y + 22),
                      fill=(70, 105, 113, 255), width=3)
    return image


def draw_illustration(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    header(draw)
    if variant == 0:
        bars(draw, 100, 265, [460, 380, 270], height=26, gap=26)
        isometric_block(draw, 930, 600, 390, 125, 95)
        isometric_block(draw, 1020, 440, 280, 105, 78)
        isometric_block(draw, 1090, 305, 180, 80, 58)
        draw.arc((790, 245, 1480, 795), 190, 345, fill=LIGHT_ACCENT, width=4)
    elif variant == 1:
        for index, (x, y, w) in enumerate(
            ((260, 635, 620), (350, 500, 500), (450, 380, 360), (545, 275, 235))
        ):
            isometric_block(
                draw, x, y, w, 78, 64,
                top=(
                    202 - index * 10,
                    215 - index * 5,
                    220 - index * 2,
                    255,
                ),
            )
            draw.line((x - 125, y + 38, x, y + 38), fill=MID, width=3)
    else:
        points = [(210, 650), (540, 520), (850, 590), (1210, 360), (1420, 470)]
        draw.line(points, fill=ACCENT, width=8)
        sizes = [120, 180, 105, 210, 90]
        for index, ((x, y), size) in enumerate(zip(points, sizes)):
            isometric_block(
                draw, x - size // 2, y, size, 58 + index * 5, 42,
                top=(190, 207, 214, 255) if index != 3 else LIGHT_ACCENT,
            )
    return image


def draw_lineart(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    header(draw)
    if variant == 0:
        bars(draw, 960, 280, [430, 340, 250], height=26, gap=28)
        draw.ellipse((160, 290, 620, 750), outline=ACCENT, width=4)
        draw.line((260, 650, 390, 405, 530, 620), fill=ACCENT, width=5)
        draw.rectangle((320, 465, 455, 600), outline=ACCENT, width=4)
        draw.line((130, 260, 230, 200), fill=LIGHT_ACCENT, width=3)
    elif variant == 1:
        draw.rectangle((130, 245, 1010, 750), outline=LIGHT_ACCENT, width=3)
        draw.ellipse((310, 340, 750, 680), outline=ACCENT, width=4)
        draw.line((530, 340, 530, 680), fill=ACCENT, width=4)
        draw.line((310, 510, 750, 510), fill=ACCENT, width=4)
        draw.line((1010, 500, 1120, 500), fill=ACCENT, width=3)
        bars(draw, 1160, 330, [250, 190, 225], color=MID, height=11, gap=52)
    else:
        draw.line((160, 585, 410, 380, 690, 570, 970, 315, 1320, 500),
                  fill=ACCENT, width=5)
        for x, y, radius in (
            (160, 585, 38), (410, 380, 55), (690, 570, 42),
            (970, 315, 70), (1320, 500, 44),
        ):
            draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                         fill=WHITE, outline=ACCENT, width=4)
        draw.line((160, 700, 1320, 700), fill=LIGHT_ACCENT, width=3)
    return image


def evidence_frame(draw, box, variant):
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=(218, 224, 226, 255), outline=INK, width=4)
    horizon = y1 + int((y2 - y1) * 0.62)
    draw.rectangle((x1 + 4, horizon, x2 - 4, y2 - 4),
                   fill=(192, 201, 204, 255))
    if variant == 0:
        draw.polygon(
            [(x1 + 100, horizon), (x1 + 350, y1 + 110),
             (x1 + 620, horizon)],
            fill=(156, 169, 174, 255),
        )
        draw.ellipse((x1 + 610, y1 + 110, x1 + 760, y1 + 260),
                     fill=LIGHT_ACCENT)
    elif variant == 1:
        draw.rectangle((x1 + 120, y1 + 120, x1 + 430, horizon),
                       fill=(163, 175, 180, 255))
        draw.polygon(
            [(x1 + 500, horizon), (x1 + 680, y1 + 180),
             (x1 + 850, horizon)],
            fill=(143, 158, 164, 255),
        )
    else:
        draw.line(
            (x1 + 90, horizon - 40, x1 + 320, y1 + 180,
             x1 + 540, horizon - 100, x1 + 820, y1 + 145),
            fill=ACCENT,
            width=9,
        )
        for x, y in (
            (x1 + 90, horizon - 40),
            (x1 + 320, y1 + 180),
            (x1 + 540, horizon - 100),
            (x1 + 820, y1 + 145),
        ):
            draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=ACCENT)


def draw_product_evidence(variant):
    image = Image.new("RGBA", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    header(draw)
    if variant == 0:
        frame = (90, 225, 1120, 735)
        evidence_frame(draw, frame, variant)
        draw.line((1160, 225, 1160, 735), fill=INK, width=4)
        bars(draw, 1210, 275, [240, 180, 260, 205], color=MID,
             height=13, gap=48)
        draw.line((640, 410, 1180, 320), fill=ACCENT, width=4)
        draw.ellipse((620, 390, 660, 430), fill=ACCENT)
    elif variant == 1:
        frame = (170, 220, 1430, 660)
        evidence_frame(draw, frame, variant)
        draw.rectangle((170, 690, 1430, 760), fill=SURFACE)
        draw.rectangle((205, 714, 250, 738), fill=ACCENT)
        draw.rectangle((285, 717, 760, 733), fill=MID)
    else:
        frame = (90, 240, 1010, 745)
        evidence_frame(draw, frame, variant)
        draw.rectangle((1060, 240, 1460, 745), outline=LIGHT_ACCENT, width=3)
        bars(draw, 1110, 295, [260, 190, 280], color=MID, height=13, gap=64)
        draw.line((740, 410, 1080, 350), fill=ACCENT, width=4)
        draw.ellipse((720, 390, 760, 430), fill=ACCENT)
    return image


DRAWERS = {
    "card-modern": draw_card_modern,
    "flat-editorial": draw_flat_editorial,
    "glass-3d": draw_glass,
    "hud-frame": draw_hud,
    "illust-2.5d": draw_illustration,
    "lineart-minimal": draw_lineart,
    "product-evidence": draw_product_evidence,
}


def expected_assets(design):
    governance = json.loads(
        (Path(design) / "governance.json").read_text(encoding="utf-8")
    )
    expected = []
    for style in sorted(governance["style_profiles"]):
        profile = governance["style_profiles"][style]
        if profile["reference_mode"] != "generated":
            continue
        for index, role in enumerate(profile["reference_roles"], 1):
            expected.append(
                {
                    "path": f"styles/{style}/ref-{index:02d}.jpg",
                    "style": style,
                    "role": role,
                }
            )
    return expected


def generate(design=DEFAULT_DESIGN):
    design = Path(design)
    assets = []
    for item in expected_assets(design):
        style = item["style"]
        index = int(Path(item["path"]).stem.split("-")[-1]) - 1
        image = DRAWERS[style](index).convert("RGB")
        path = design / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(
            path,
            format="JPEG",
            quality=92,
            subsampling=0,
            optimize=False,
            progressive=False,
        )
        assets.append(
            {
                **item,
                "width": WIDTH,
                "height": HEIGHT,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "version": 1,
        "generator": "scripts/generate_style_refs.py",
        "rules": {
            "text_free": True,
            "brand_free": True,
            "data_free": True,
            "palette_neutral": True,
        },
        "assets": assets,
    }
    (design / "reference-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def validate_assets(design=DEFAULT_DESIGN):
    design = Path(design)
    errors = []
    manifest_path = design / "reference-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"reference-manifest.json 无法读取: {exc}"]
    required_rules = {
        "text_free": True,
        "brand_free": True,
        "data_free": True,
        "palette_neutral": True,
    }
    if manifest.get("rules") != required_rules:
        errors.append("reference-manifest.json: rules 必须声明四项中性资产保证")
    try:
        expected = expected_assets(design)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return errors + [f"governance.json 无法解析参考资产配置: {exc}"]
    expected_paths = {item["path"] for item in expected}
    entries = manifest.get("assets", [])
    if not isinstance(entries, list):
        return errors + ["reference-manifest.json: assets 必须是数组"]
    valid_entries = []
    for item in entries:
        if not isinstance(item, dict):
            errors.append("reference-manifest.json: manifest 资产条目必须是对象")
            continue
        valid_entries.append(item)
    actual_paths = {
        item.get("path") for item in valid_entries
    }
    if actual_paths != expected_paths:
        errors.append(
            f"reference-manifest.json: 资产集合不一致 "
            f"missing={sorted(expected_paths - actual_paths)} "
            f"extra={sorted(actual_paths - expected_paths)}"
        )
    if len(actual_paths) != len(valid_entries):
        errors.append("reference-manifest.json: 资产 path 不得缺失或重复")
    role_map = {item["path"]: item["role"] for item in expected}
    style_map = {item["path"]: item["style"] for item in expected}
    for item in valid_entries:
        relative = item.get("path", "")
        if not isinstance(relative, str) or not relative:
            errors.append("reference-manifest.json: 资产 path 必须是非空字符串")
            continue
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            errors.append(f"{relative}: 资产 path 必须位于 design 目录内")
            continue
        path = design / relative
        if not path.is_file():
            errors.append(f"{relative}: 文件不存在")
            continue
        try:
            with Image.open(path) as image:
                if image.format != "JPEG":
                    errors.append(f"{relative}: 必须为 JPEG")
                if image.size != (WIDTH, HEIGHT):
                    errors.append(
                        f"{relative}: 尺寸 {image.size}，应为 {(WIDTH, HEIGHT)}"
                    )
                if image.getexif():
                    errors.append(f"{relative}: 不得包含 EXIF")
        except OSError as exc:
            errors.append(f"{relative}: 图片无法读取: {exc}")
            continue
        if item.get("width") != WIDTH or item.get("height") != HEIGHT:
            errors.append(f"{relative}: manifest 尺寸字段不正确")
        if item.get("role") != role_map.get(relative):
            errors.append(f"{relative}: role 与 governance.json 不一致")
        if item.get("style") != style_map.get(relative):
            errors.append(f"{relative}: style 与 governance.json 不一致")
        if item.get("sha256") != sha256(path):
            errors.append(f"{relative}: sha256 不匹配")
    generated_styles = {item["style"] for item in expected}
    missing_drawers = generated_styles - set(DRAWERS)
    if missing_drawers:
        errors.append(
            f"以下 generated 风格缺少绘图器: {sorted(missing_drawers)}"
        )
    for style in DRAWERS:
        expected_for_style = {
            design / item["path"]
            for item in expected
            if item["style"] == style
        }
        actual_for_style = set((design / "styles" / style).glob("ref-*.jpg"))
        if actual_for_style != expected_for_style:
            errors.append(f"styles/{style}: ref 文件集合与 manifest 不一致")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", default=str(DEFAULT_DESIGN))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = validate_assets(args.design)
        if errors:
            print("[generate_style_refs] CHECK FAILED")
            for error in errors:
                print(" - " + error)
            return 1
        count = len(expected_assets(args.design))
        print(
            f"[generate_style_refs] CHECK PASSED: {count} neutral references"
        )
        return 0
    manifest = generate(args.design)
    print(
        f"[generate_style_refs] generated {len(manifest['assets'])} "
        f"neutral references"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
