#!/usr/bin/env python3

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RENDER_VERSION = "pillow-v2.0.0-no-fallback"
SKILL_DIR = Path(__file__).resolve().parents[1]
CONTRACT_PATH = SKILL_DIR / "layout_contract.json"
TEMPLATE_REGISTRY_PATH = SKILL_DIR / "template_registry.json"
CONFIG_PATH = SKILL_DIR / "config" / "global_defaults.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_file(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_relative_to(path: Path, root: Path):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def text_len(text):
    return len([c for c in str(text).strip() if not c.isspace()])


def pick_font(size, font_path):
    path = Path(font_path).expanduser()
    if path.exists():
        font = ImageFont.truetype(str(path), size=size)
        return font, str(path), font.getname()
    raise FileNotFoundError(f"Locked font does not exist: {path}")


def rgba(value, fallback=(0, 0, 0, 180)):
    value = str(value).strip()
    if value.startswith("#") and len(value) == 7:
        return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5)) + (255,)
    if value.startswith("rgba(") and value.endswith(")"):
        parts = [p.strip() for p in value[5:-1].split(",")]
        if len(parts) == 4:
            return (int(parts[0]), int(parts[1]), int(parts[2]), int(float(parts[3]) * 255))
    return fallback


def fit_contract_fonts(layout, sidecar):
    title = dict(layout["title"])
    subtitle = dict(layout["subtitle"])
    variants = layout.get("title_package", {}).get("char_variants", {})
    if variants:
        key = str(min(max(text_len(sidecar["main_title"]), 2), max(map(int, variants.keys()))))
        variant = variants.get(key)
        if variant:
            title["font_size"] = variant.get("title_font_size", title["font_size"])
            subtitle["font_size"] = variant.get("subtitle_font_size", subtitle["font_size"])
    return title, subtitle


def apply_soft_zone_cleanup(image, package):
    cleanup = (package or {}).get("soft_zone_cleanup", {})
    if not cleanup.get("enabled"):
        return image

    x = cleanup.get("x", package.get("x", 0))
    y = cleanup.get("y", package.get("y", 0))
    w = cleanup.get("width", package.get("width", image.width))
    h = cleanup.get("height", package.get("height", image.height))
    radius = cleanup.get("radius", package.get("backing_radius", 22))
    max_alpha = cleanup.get("max_alpha", 188)
    border_alpha = cleanup.get("border_alpha", 50)
    bottom_feather = cleanup.get("bottom_feather", 0)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=max_alpha)

    if bottom_feather > 0:
        start = max(y, y + h - bottom_feather)
        for row in range(start, y + h + 1):
            t = (row - start) / max(bottom_feather, 1)
            alpha = int(max_alpha * (1 - t))
            mask_draw.line((x, row, x + w, row), fill=alpha)

    glass = Image.new("RGBA", image.size, (3, 12, 21, 255))
    glass.putalpha(mask)
    overlay = Image.alpha_composite(overlay, glass)

    border = ImageDraw.Draw(overlay)
    border.rounded_rectangle(
        (x, y, x + w, y + h),
        radius=radius,
        outline=(78, 167, 240, border_alpha),
        width=2,
    )
    return Image.alpha_composite(image, overlay)


def text_position(draw, box, text, font, stroke_width, visual_top=None, align="center"):
    x, y, w, h = box
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    if align == "left":
        tx = x - bbox[0]
    elif align == "right":
        tx = x + w - tw - bbox[0]
    else:
        tx = x + (w - tw) / 2 - bbox[0]
    if visual_top is None:
        ty = y + (h - th) / 2 - bbox[1]
    else:
        ty = visual_top - bbox[1]
    return tx, ty, tw, th


def draw_text_at(draw, position, text, font, fill, stroke_fill, stroke_width, shadow=True):
    tx, ty = position

    if shadow:
        draw.text(
            (tx + 8, ty + 10),
            text,
            font=font,
            fill=(0, 0, 0, 180),
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0, 210),
        )

    if not shadow and stroke_width == 0:
        draw.text((tx, ty), text, font=font, fill=fill)
        return

    # Fake weight without CSS blur only when readability effects are enabled.
    offsets = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    for ox, oy in offsets:
        draw.text((tx + ox, ty + oy), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def rendered_bbox(draw, position, text, font, stroke_width):
    bbox = draw.textbbox(position, text, font=font, stroke_width=stroke_width)
    return {
        "x": round(bbox[0], 2),
        "y": round(bbox[1], 2),
        "width": round(bbox[2] - bbox[0], 2),
        "height": round(bbox[3] - bbox[1], 2),
        "right": round(bbox[2], 2),
        "bottom": round(bbox[3], 2),
    }


def draw_centered_text(draw, box, text, font, fill, stroke_fill, stroke_width, shadow=True, align="center"):
    tx, ty, _, _ = text_position(draw, box, text, font, stroke_width, align=align)
    draw_text_at(draw, (tx, ty), text, font, fill, stroke_fill, stroke_width, shadow=shadow)


def render(args):
    sidecar_path = Path(args.sidecar).resolve()
    background_path = Path(args.background).resolve()
    out_dir = Path(args.out).resolve()

    contract = read_json(CONTRACT_PATH)
    templates = read_json(TEMPLATE_REGISTRY_PATH)["templates"]
    config = read_json(CONFIG_PATH)
    if not args.manifest:
        raise ValueError("Final rendering requires --manifest. No fallback manifest discovery is allowed.")
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(f"Required run manifest does not exist: {manifest_path}")
    manifest = read_json(manifest_path)
    sidecar = read_json(sidecar_path)
    platform = args.platform or sidecar["platform"]
    sidecar["platform"] = platform

    if platform not in manifest.get("channels", {}):
        raise ValueError(f"Platform {platform} is not locked in run_manifest.lock.json")
    manifest_out_dir = Path(manifest["output_dir"]).resolve()
    if out_dir != manifest_out_dir:
        raise ValueError(f"Output directory drift: --out={out_dir} manifest.output_dir={manifest_out_dir}")

    palette = manifest.get("palette_lock", config["palette_lock"])
    fonts = manifest.get("fonts", config["fonts"])
    template_id = manifest.get("template_id", sidecar.get("template_id") or config["default_template_id"])
    if sidecar.get("template_id") and sidecar["template_id"] != template_id:
        raise ValueError(f"Template drift: sidecar={sidecar['template_id']} locked={template_id}")
    sidecar["template_id"] = template_id

    output_root = Path(manifest.get("output_root") or config["output_root"]).resolve()
    if config["hard_failures"].get("forbid_output_outside_root") and not is_relative_to(out_dir, output_root):
        raise ValueError(f"Output directory is outside locked root: {out_dir} not under {output_root}")

    if not palette.get("allow_auto_text_color_change", False):
        title_fill = rgba(palette["title_fill"])
        subtitle_fill = rgba(palette["subtitle_fill"])
    else:
        template = templates[template_id]
        title_fill = rgba(template["title_color"])
        subtitle_fill = rgba(template["subtitle_color"])

    out_dir.mkdir(parents=True, exist_ok=True)

    layout = contract["platforms"][platform]
    template = templates[template_id]
    title, subtitle = fit_contract_fonts(layout, sidecar)

    image = Image.open(background_path).convert("RGBA")
    canvas = layout["canvas"]
    if image.size != (canvas["width"], canvas["height"]):
        image = image.resize((canvas["width"], canvas["height"]), Image.Resampling.LANCZOS)

    package = layout.get("title_package", {})
    image = apply_soft_zone_cleanup(image, package)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if package and package.get("backing"):
        px, py, pw, ph = package["x"], package["y"], package["width"], package["height"]
        draw.rounded_rectangle(
            (px, py, px + pw, py + ph),
            radius=package.get("backing_radius", 22),
            fill=rgba(package.get("backing_color", "rgba(0,0,0,0.72)")),
        )

    title_font, title_font_path, title_font_name = pick_font(
        title["font_size"],
        fonts["title_font_path"],
    )
    subtitle_font, subtitle_font_path, subtitle_font_name = pick_font(
        subtitle["font_size"],
        fonts["subtitle_font_path"],
    )
    stroke = rgba(template["stroke_color"])

    title_group = package.get("title_group", {})
    rendered_text = {}
    if title_group.get("vertical_center_mode") == "bbox_equal_margin":
        title_box = (title["x"], title["y"], title["width"], title["height"])
        subtitle_box = (subtitle["x"], subtitle["y"], subtitle["width"], subtitle["height"])
        _, _, _, title_h = text_position(draw, title_box, sidecar["main_title"], title_font, title["stroke_width"], align=title.get("align", "center"))
        _, _, _, subtitle_h = text_position(draw, subtitle_box, sidecar["sub_title"], subtitle_font, subtitle["stroke_width"], align=subtitle.get("align", "center"))
        frame_top = title_group.get("frame_top", package.get("y", 0))
        frame_bottom = title_group.get("frame_bottom", package.get("y", 0) + package.get("height", 0))
        gap = title_group.get("gap", 24)
        group_height = title_h + gap + subtitle_h
        group_top = frame_top + ((frame_bottom - frame_top) - group_height) / 2
        title_tx, title_ty, _, _ = text_position(
            draw,
            title_box,
            sidecar["main_title"],
            title_font,
            title["stroke_width"],
            visual_top=group_top,
            align=title.get("align", "center"),
        )
        subtitle_tx, subtitle_ty, _, _ = text_position(
            draw,
            subtitle_box,
            sidecar["sub_title"],
            subtitle_font,
            subtitle["stroke_width"],
            visual_top=group_top + title_h + gap,
            align=subtitle.get("align", "center"),
        )
        draw_text_at(draw, (title_tx, title_ty), sidecar["main_title"], title_font, title_fill, stroke, title["stroke_width"], shadow=title.get("shadow", True))
        draw_text_at(draw, (subtitle_tx, subtitle_ty), sidecar["sub_title"], subtitle_font, subtitle_fill, stroke, subtitle["stroke_width"], shadow=subtitle.get("shadow", True))
        rendered_text = {
            "title_bbox": rendered_bbox(draw, (title_tx, title_ty), sidecar["main_title"], title_font, title["stroke_width"]),
            "subtitle_bbox": rendered_bbox(draw, (subtitle_tx, subtitle_ty), sidecar["sub_title"], subtitle_font, subtitle["stroke_width"]),
        }
    else:
        title_tx, title_ty, _, _ = text_position(
            draw,
            (title["x"], title["y"], title["width"], title["height"]),
            sidecar["main_title"],
            title_font,
            title["stroke_width"],
            align=title.get("align", "center"),
        )
        subtitle_tx, subtitle_ty, _, _ = text_position(
            draw,
            (subtitle["x"], subtitle["y"], subtitle["width"], subtitle["height"]),
            sidecar["sub_title"],
            subtitle_font,
            subtitle["stroke_width"],
            align=subtitle.get("align", "center"),
        )
        draw_centered_text(
            draw,
            (title["x"], title["y"], title["width"], title["height"]),
            sidecar["main_title"],
            title_font,
            title_fill,
            stroke,
            title["stroke_width"],
            shadow=title.get("shadow", True),
            align=title.get("align", "center"),
        )
        draw_centered_text(
            draw,
            (subtitle["x"], subtitle["y"], subtitle["width"], subtitle["height"]),
            sidecar["sub_title"],
            subtitle_font,
            subtitle_fill,
            stroke,
            subtitle["stroke_width"],
            shadow=subtitle.get("shadow", True),
            align=subtitle.get("align", "center"),
        )
        rendered_text = {
            "title_bbox": rendered_bbox(draw, (title_tx, title_ty), sidecar["main_title"], title_font, title["stroke_width"]),
            "subtitle_bbox": rendered_bbox(draw, (subtitle_tx, subtitle_ty), sidecar["sub_title"], subtitle_font, subtitle["stroke_width"]),
        }

    result = Image.alpha_composite(image, overlay).convert("RGB")
    final_path = out_dir / f"{platform}_final_pillow.png"
    sidecar_out = out_dir / f"{platform}_sidecar_pillow.json"
    trace_out = out_dir / f"{platform}_trace_pillow.json"
    result.save(final_path, "PNG")
    write_json(sidecar_out, sidecar)

    trace = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform,
        "content_id": sidecar["content_id"],
        "template_id": template_id,
        "layout_contract_version": contract["version"],
        "render_version": RENDER_VERSION,
        "renderer": "Pillow/Freetype deterministic text compositor",
        "manifest": {
            "path": str(manifest_path) if manifest_path.exists() else None,
            "sha256": sha256_file(manifest_path) if manifest_path.exists() else None,
        },
        "text_color": {
            "title_fill": palette["title_fill"],
            "subtitle_fill": palette["subtitle_fill"],
            "allow_auto_text_color_change": bool(palette.get("allow_auto_text_color_change")),
        },
        "font": {
            "title_font_path": title_font_path,
            "title_font_name": title_font_name,
            "subtitle_font_path": subtitle_font_path,
            "subtitle_font_name": subtitle_font_name,
        },
        "output": {
            "final_png": str(final_path),
            "sidecar_json": str(sidecar_out),
            "trace_json": str(trace_out),
        },
        "rendered_text": rendered_text,
        "hashes": {
            "sidecar_sha256": hashlib.sha256(json.dumps(sidecar, ensure_ascii=False).encode("utf-8")).hexdigest(),
            "global_defaults_sha256": sha256_file(CONFIG_PATH),
            "layout_contract_sha256": sha256_file(CONTRACT_PATH),
            "template_registry_sha256": sha256_file(TEMPLATE_REGISTRY_PATH),
            "background_sha256": sha256_file(background_path),
            "final_png_sha256": sha256_file(final_path),
        },
        "qa": {
            "passed": True,
            "main_title_length": text_len(sidecar["main_title"]),
            "sub_title_length": text_len(sidecar["sub_title"]),
            "output_size": canvas,
            "text_renderer": "pillow",
        },
    }
    write_json(trace_out, trace)
    print(json.dumps(trace["output"], ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--out", required=True)
    render(parser.parse_args())


if __name__ == "__main__":
    main()
