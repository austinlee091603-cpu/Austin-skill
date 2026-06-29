#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_DIR / "config" / "global_defaults.json"
LAYOUT_PATH = SKILL_DIR / "layout_contract.json"
AVATAR_PATH = SKILL_DIR / "avatar_bible.json"
RENDERER = SKILL_DIR / "render" / "render_cover_pillow.py"
QA_SCRIPT = SKILL_DIR / "scripts" / "qa_cover.py"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_skill_asset(raw_path):
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = SKILL_DIR / path
    return path.resolve()


def normalize_config(config):
    normalized = json.loads(json.dumps(config, ensure_ascii=False))
    for key in ["title_font_path", "subtitle_font_path"]:
        normalized["fonts"][key] = str(resolve_skill_asset(normalized["fonts"][key]))
    return normalized


def parse_platform_paths(values, label):
    result = {}
    for value in values:
        if ":" not in value:
            raise SystemExit(f"Invalid --{label} value {value!r}; expected platform:/absolute/path")
        platform, raw_path = value.split(":", 1)
        platform = platform.strip()
        path = Path(raw_path).expanduser().resolve()
        if not platform:
            raise SystemExit(f"Invalid --{label} platform in {value!r}")
        if not path.exists():
            raise SystemExit(f"Missing --{label} file for {platform}: {path}")
        result[platform] = path
    return result


def text_len(text):
    return len([c for c in str(text).strip() if not c.isspace()])


def validate_locked_assets(config, avatar_bible):
    failures = []
    for key in ["title_font_path", "subtitle_font_path"]:
        path = resolve_skill_asset(config["fonts"][key])
        if not path.exists():
            failures.append(f"locked font missing: {key}={path}")
    avatar_ref = resolve_skill_asset(avatar_bible["default_reference_image"])
    if not avatar_ref.exists():
        failures.append(f"locked avatar reference missing: {avatar_ref}")
    output_root = Path(config["output_root"]).expanduser()
    if not output_root.exists():
        output_root.mkdir(parents=True, exist_ok=True)
    if failures:
        raise SystemExit("\n".join(failures))


def validate_sidecar(platform, sidecar, layout, config):
    failures = []
    if sidecar.get("platform") != platform:
        failures.append(f"{platform}: sidecar.platform={sidecar.get('platform')!r}")
    if sidecar.get("template_id") != config["default_template_id"]:
        failures.append(f"{platform}: template_id must be {config['default_template_id']}")
    platform_layout = layout["platforms"][platform]
    if text_len(sidecar.get("main_title", "")) > platform_layout["title"]["max_chars"]:
        failures.append(f"{platform}: main_title exceeds locked max chars")
    if text_len(sidecar.get("sub_title", "")) > platform_layout["subtitle"]["max_chars"]:
        failures.append(f"{platform}: sub_title exceeds locked max chars")

    constraints = sidecar.get("constraints") or {}
    for key in ["lock_text_layout", "no_big_head", "no_text_generated_by_model", "semantic_object_lock"]:
        if constraints.get(key) is not True:
            failures.append(f"{platform}: constraints.{key} must be true")
    if platform == "douyin_xhs_landscape":
        for key in ["no_hard_crop", "independent_horizontal_composition", "center_top_title_system", "adversarial_review_complete"]:
            if constraints.get(key) is not True:
                failures.append(f"{platform}: constraints.{key} must be true")
    if platform == "wechat":
        for key in ["left_50_text_zone", "right_50_visual_zone", "soft_transition_band", "no_text_cross_50_percent_boundary"]:
            if constraints.get(key) is not True:
                failures.append(f"{platform}: constraints.{key} must be true")

    avatar = sidecar.get("avatar") or {}
    avatar_ref = avatar.get("reference_image")
    if not avatar_ref or not resolve_skill_asset(avatar_ref).exists():
        failures.append(f"{platform}: avatar.reference_image is missing or does not exist")
    if not avatar.get("locked_traits"):
        failures.append(f"{platform}: avatar.locked_traits is required")

    resolver = sidecar.get("visual_object_resolver")
    if not isinstance(resolver, dict):
        failures.append(f"{platform}: visual_object_resolver is required")
        resolver = {}
    for key in ["semantic_frame", "task_object", "primary_visual_object", "visual_metaphor"]:
        if not str(resolver.get(key, "")).strip():
            failures.append(f"{platform}: visual_object_resolver.{key} is required")
    for key in ["allowed_objects", "forbidden_objects", "misread_risks"]:
        value = resolver.get(key)
        if not isinstance(value, list) or not value:
            failures.append(f"{platform}: visual_object_resolver.{key} must be a non-empty list")
    rules = resolver.get("prompt_object_rules") or {}
    for key in ["must_include", "must_exclude"]:
        value = rules.get(key)
        if not isinstance(value, list) or not value:
            failures.append(f"{platform}: prompt_object_rules.{key} must be a non-empty list")

    image_prompt = sidecar.get("image_prompt") or {}
    background_prompt = str(image_prompt.get("background_prompt", "")).lower()
    negative_prompt = str(image_prompt.get("negative_prompt", "")).lower()
    for term in rules.get("must_include", []) if isinstance(rules.get("must_include"), list) else []:
        if term.lower() not in background_prompt:
            failures.append(f"{platform}: must_include missing from background_prompt: {term}")
    for term in rules.get("must_exclude", []) if isinstance(rules.get("must_exclude"), list) else []:
        if term.lower() not in negative_prompt:
            failures.append(f"{platform}: must_exclude missing from negative_prompt: {term}")

    if failures:
        raise SystemExit("\n".join(failures))


def create_manifest(run_id, channels, sidecars, script_file, config, layout):
    output_root = Path(config["output_root"]).expanduser().resolve()
    output_dir = output_root / run_id
    manifest = {
        "manifest_version": "v2.0.0-no-fallback",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "content_id": run_id,
        "skill": "social-media-cover",
        "template_id": config["default_template_id"],
        "output_root": str(output_root),
        "output_dir": str(output_dir),
        "palette_lock": config["palette_lock"],
        "fonts": config["fonts"],
        "channels": {},
        "source": {
            "script_file": str(script_file.resolve()) if script_file else None
        },
        "policy": {
            "template_locked": True,
            "palette_locked": True,
            "output_root_locked": True,
            "font_locked": True,
            "no_fallback": True,
            "text_color_override_allowed": False
        }
    }
    for platform in channels:
        sidecar = sidecars[platform]
        platform_layout = layout["platforms"][platform]
        manifest["channels"][platform] = {
            "platform": platform,
            "size": config["channels"][platform]["size"],
            "aspect": config["channels"][platform]["aspect"],
            "main_title": sidecar["main_title"],
            "sub_title": sidecar["sub_title"],
            "title_bbox": platform_layout["title"],
            "subtitle_bbox": platform_layout["subtitle"],
            "title_safe_zone": config["channels"][platform]["title_safe_zone"],
            "title_safe_zone_quality": config["channels"][platform]["title_safe_zone_quality"]
        }
    return manifest


def copy_background(platform, source, output_dir):
    destination = output_dir / f"{platform}_background.png"
    if source != destination:
        shutil.copy2(source, destination)
    return destination


def run_command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stdout)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="No-fallback final delivery pipeline for Social Media Cover.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--channels", required=True, help="Comma-separated platforms, e.g. douyin,wechat")
    parser.add_argument("--script-file", default=None)
    parser.add_argument("--sidecar", action="append", required=True, help="platform:/path/to/sidecar.json")
    parser.add_argument("--background", action="append", required=True, help="platform:/path/to/textless_background.png")
    args = parser.parse_args()

    config = read_json(CONFIG_PATH)
    layout = read_json(LAYOUT_PATH)
    avatar_bible = read_json(AVATAR_PATH)
    validate_locked_assets(config, avatar_bible)
    config = normalize_config(config)

    channels = [item.strip() for item in args.channels.split(",") if item.strip()]
    if not channels:
        raise SystemExit("--channels must include at least one platform")
    for channel in channels:
        if channel not in config["channels"] or channel not in layout["platforms"]:
            raise SystemExit(f"Unknown channel: {channel}")

    sidecar_paths = parse_platform_paths(args.sidecar, "sidecar")
    background_paths = parse_platform_paths(args.background, "background")
    missing_sidecars = sorted(set(channels) - set(sidecar_paths))
    missing_backgrounds = sorted(set(channels) - set(background_paths))
    if missing_sidecars:
        raise SystemExit(f"Missing sidecars for channels: {', '.join(missing_sidecars)}")
    if missing_backgrounds:
        raise SystemExit(f"Missing backgrounds for channels: {', '.join(missing_backgrounds)}")

    sidecars = {}
    for platform in channels:
        sidecar = read_json(sidecar_paths[platform])
        validate_sidecar(platform, sidecar, layout, config)
        sidecars[platform] = sidecar

    script_file = Path(args.script_file).expanduser().resolve() if args.script_file else None
    if script_file and not script_file.exists():
        raise SystemExit(f"Missing script file: {script_file}")

    manifest = create_manifest(args.run_id, channels, sidecars, script_file, config, layout)
    output_dir = Path(manifest["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "run_manifest.lock.json"
    write_json(manifest_path, manifest)

    results = {}
    for platform in channels:
        planned_sidecar_path = output_dir / f"{platform}_sidecar_planned.json"
        write_json(planned_sidecar_path, sidecars[platform])
        background_path = copy_background(platform, background_paths[platform], output_dir)

        run_command([
            sys.executable,
            str(RENDERER),
            "--manifest",
            str(manifest_path),
            "--sidecar",
            str(planned_sidecar_path),
            "--background",
            str(background_path),
            "--platform",
            platform,
            "--out",
            str(output_dir),
        ])

        final_path = output_dir / f"{platform}_final_pillow.png"
        trace_path = output_dir / f"{platform}_trace_pillow.json"
        qa_report_path = output_dir / f"{platform}_qa_report.json"
        run_command([
            sys.executable,
            str(QA_SCRIPT),
            "--manifest",
            str(manifest_path),
            "--sidecar",
            str(output_dir / f"{platform}_sidecar_pillow.json"),
            "--trace",
            str(trace_path),
            "--background",
            str(background_path),
            "--final",
            str(final_path),
            "--platform",
            platform,
            "--out",
            str(qa_report_path),
        ])

        results[platform] = {
            "background": str(background_path),
            "final_png": str(final_path),
            "sidecar_json": str(output_dir / f"{platform}_sidecar_pillow.json"),
            "trace_json": str(trace_path),
            "qa_report": str(qa_report_path)
        }

    pipeline_report = {
        "passed": True,
        "run_id": args.run_id,
        "manifest": str(manifest_path),
        "channels": results,
        "no_fallback": True
    }
    report_path = output_dir / "pipeline_report.json"
    write_json(report_path, pipeline_report)
    print(json.dumps(pipeline_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
