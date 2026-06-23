#!/usr/bin/env python3

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageFilter


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_DIR / "config" / "global_defaults.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def is_relative_to(path: Path, root: Path):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def text_len(text):
    return len([c for c in str(text).strip() if not c.isspace()])


def crop_safe_zone(image: Image.Image, zone):
    x, y, w, h = zone["x"], zone["y"], zone["width"], zone["height"]
    return image.crop((x, y, x + w, y + h)).convert("RGB")


def image_pixels(image: Image.Image):
    if hasattr(image, "get_flattened_data"):
        return list(image.get_flattened_data())
    return list(image.getdata())


def safe_zone_metrics(background_path: Path, zone):
    crop = crop_safe_zone(Image.open(background_path), zone)
    pixels = image_pixels(crop)
    count = max(len(pixels), 1)
    mean_luma = sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels) / count
    yellow_pixels = sum(1 for r, g, b in pixels if r > 170 and g > 135 and b < 95 and (r - b) > 90)
    yellow_ratio = yellow_pixels / count

    edges = crop.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_pixels = image_pixels(edges)
    edge_density = sum(1 for p in edge_pixels if p > 36) / len(edge_pixels)

    width, height = crop.size
    border = max(8, min(width, height) // 35)
    border_values = []
    center_values = []
    for y in range(height):
        for x in range(width):
            value = edge_pixels[y * width + x]
            if x < border or y < border or x >= width - border or y >= height - border:
                border_values.append(value)
            else:
                center_values.append(value)
    border_mean = sum(border_values) / max(len(border_values), 1)
    center_mean = sum(center_values) / max(len(center_values), 1)
    if edge_density < 0.01:
        border_edge_ratio = 0.0
    else:
        border_edge_ratio = border_mean / max(center_mean, 1)

    return {
        "mean_luma": round(mean_luma, 3),
        "yellow_pixel_ratio": round(yellow_ratio, 5),
        "edge_density": round(edge_density, 5),
        "border_edge_ratio": round(border_edge_ratio, 5)
    }


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _nonempty_string_list(value, min_items=1):
    return (
        isinstance(value, list)
        and len(value) >= min_items
        and all(_nonempty_string(item) for item in value)
    )


def validate_visual_object_resolver(sidecar):
    failures = []
    warnings = []
    resolver = sidecar.get("visual_object_resolver")
    if not isinstance(resolver, dict):
        return ["missing visual_object_resolver"], warnings

    for key in ["semantic_frame", "task_object", "primary_visual_object", "visual_metaphor"]:
        if not _nonempty_string(resolver.get(key)):
            failures.append(f"visual_object_resolver.{key} is missing or empty")

    if not _nonempty_string_list(resolver.get("allowed_objects"), min_items=2):
        failures.append("visual_object_resolver.allowed_objects must contain at least two strings")
    if not _nonempty_string_list(resolver.get("forbidden_objects"), min_items=1):
        failures.append("visual_object_resolver.forbidden_objects must contain at least one string")
    if not _nonempty_string_list(resolver.get("misread_risks"), min_items=1):
        failures.append("visual_object_resolver.misread_risks must contain at least one string")

    rules = resolver.get("prompt_object_rules")
    if not isinstance(rules, dict):
        failures.append("visual_object_resolver.prompt_object_rules is missing")
        rules = {}
    must_include = rules.get("must_include")
    must_exclude = rules.get("must_exclude")
    if not _nonempty_string_list(must_include, min_items=1):
        failures.append("prompt_object_rules.must_include must contain at least one string")
        must_include = []
    if not _nonempty_string_list(must_exclude, min_items=1):
        failures.append("prompt_object_rules.must_exclude must contain at least one string")
        must_exclude = []

    semantic_qa = resolver.get("semantic_qa")
    if not isinstance(semantic_qa, dict):
        failures.append("visual_object_resolver.semantic_qa is missing")
    else:
        for key in ["first_read_should_be", "must_not_read_as"]:
            if not _nonempty_string(semantic_qa.get(key)):
                failures.append(f"semantic_qa.{key} is missing or empty")
        if semantic_qa.get("manual_check_required") is not True:
            warnings.append("semantic_qa.manual_check_required should be true for image2 backgrounds")

    image_prompt = sidecar.get("image_prompt") or {}
    background_prompt = str(image_prompt.get("background_prompt", "")).lower()
    negative_prompt = str(image_prompt.get("negative_prompt", "")).lower()
    primary = str(resolver.get("primary_visual_object", "")).lower()
    if primary and primary not in background_prompt:
        warnings.append("primary_visual_object is not quoted verbatim in background_prompt; verify the prompt still expresses it")
    for term in must_include:
        if term.lower() not in background_prompt:
            failures.append(f"must_include term missing from background_prompt: {term}")
    for term in must_exclude:
        if term.lower() not in negative_prompt:
            failures.append(f"must_exclude term missing from negative_prompt: {term}")

    constraints = sidecar.get("constraints") or {}
    if constraints.get("semantic_object_lock") is not True:
        failures.append("constraints.semantic_object_lock must be true")

    return failures, warnings


def main():
    parser = argparse.ArgumentParser(description="Blocking QA for Social Media Cover outputs.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--final", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    config = read_json(CONFIG_PATH)
    manifest = read_json(Path(args.manifest))
    sidecar = read_json(Path(args.sidecar))
    trace = read_json(Path(args.trace))
    platform = args.platform
    failures = []
    warnings = []

    if platform not in manifest["channels"]:
        failures.append(f"{platform}: missing from run_manifest.lock.json")
        channel = None
    else:
        channel = manifest["channels"][platform]

    final_path = Path(args.final).resolve()
    background_path = Path(args.background).resolve()
    output_root = Path(manifest.get("output_root") or config["output_root"]).resolve()
    if config["hard_failures"].get("forbid_output_outside_root") and not is_relative_to(final_path, output_root):
        failures.append(f"final output outside locked root: {final_path} not under {output_root}")

    if sidecar.get("template_id") != manifest.get("template_id"):
        failures.append(f"template drift: sidecar={sidecar.get('template_id')} manifest={manifest.get('template_id')}")
    if trace.get("template_id") != manifest.get("template_id"):
        failures.append(f"trace template drift: trace={trace.get('template_id')} manifest={manifest.get('template_id')}")

    trace_colors = trace.get("text_color", {})
    palette = manifest.get("palette_lock", config["palette_lock"])
    if trace_colors.get("title_fill") != palette["title_fill"]:
        failures.append(f"title color drift: trace={trace_colors.get('title_fill')} locked={palette['title_fill']}")
    if trace_colors.get("subtitle_fill") != palette["subtitle_fill"]:
        failures.append(f"subtitle color drift: trace={trace_colors.get('subtitle_fill')} locked={palette['subtitle_fill']}")

    font = trace.get("font", {})
    fonts = manifest.get("fonts", config["fonts"])
    if font.get("title_font_path") != fonts["title_font_path"]:
        failures.append(f"title font drift: trace={font.get('title_font_path')} locked={fonts['title_font_path']}")
    if font.get("subtitle_font_path") != fonts["subtitle_font_path"]:
        failures.append(f"subtitle font drift: trace={font.get('subtitle_font_path')} locked={fonts['subtitle_font_path']}")

    resolver_failures, resolver_warnings = validate_visual_object_resolver(sidecar)
    failures.extend(resolver_failures)
    warnings.extend(resolver_warnings)

    if channel:
        final_image = Image.open(final_path)
        expected_size = tuple(channel["size"])
        if final_image.size != expected_size:
            failures.append(f"wrong final size: {final_image.size} != {expected_size}")
        max_main = channel["title_bbox"]["max_chars"]
        max_sub = channel["subtitle_bbox"]["max_chars"]
        if text_len(sidecar.get("main_title", "")) > max_main:
            failures.append("main title overflow")
        if text_len(sidecar.get("sub_title", "")) > max_sub:
            failures.append("subtitle overflow")

        metrics = safe_zone_metrics(background_path, channel["title_safe_zone"])
        quality = channel["title_safe_zone_quality"]
        if metrics["mean_luma"] > quality["max_mean_luma"]:
            failures.append(f"title safe zone too bright: {metrics['mean_luma']} > {quality['max_mean_luma']}")
        if metrics["yellow_pixel_ratio"] > quality["max_yellow_pixel_ratio"]:
            failures.append(f"title safe zone yellow glow: {metrics['yellow_pixel_ratio']} > {quality['max_yellow_pixel_ratio']}")
        if metrics["edge_density"] > quality["max_edge_density"]:
            failures.append(f"title safe zone too busy: {metrics['edge_density']} > {quality['max_edge_density']}")
        if metrics["border_edge_ratio"] > quality["max_border_edge_ratio"]:
            failures.append(f"title safe zone likely has large frame: {metrics['border_edge_ratio']} > {quality['max_border_edge_ratio']}")
    else:
        metrics = {}

    report = {
        "passed": not failures,
        "platform": platform,
        "failures": failures,
        "warnings": warnings,
        "metrics": metrics,
        "final_png": str(final_path),
        "background": str(background_path)
    }
    report_path = Path(args.out).resolve() if args.out else final_path.parent / f"{platform}_qa_report.json"
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
