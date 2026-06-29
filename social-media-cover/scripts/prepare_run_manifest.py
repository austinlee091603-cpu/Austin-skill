#!/usr/bin/env python3

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_DIR / "config" / "global_defaults.json"
LAYOUT_PATH = SKILL_DIR / "layout_contract.json"


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


def sha256_text(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_channel_titles(values):
    titles = {}
    for value in values or []:
        parts = value.split(":", 2)
        if len(parts) != 3:
            raise SystemExit(f"Invalid --channel-title value: {value!r}; expected platform:main:subtitle")
        platform, main_title, sub_title = parts
        titles[platform] = {"main_title": main_title, "sub_title": sub_title}
    return titles


def main():
    parser = argparse.ArgumentParser(description="Create locked Social Media Cover run manifest.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--channels", required=True, help="Comma-separated platforms, e.g. douyin,wechat")
    parser.add_argument("--content-id", default=None)
    parser.add_argument("--template-id", default=None)
    parser.add_argument("--channel-title", action="append", default=[], help="platform:main_title:sub_title")
    parser.add_argument("--script-file", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--out", default=None, help="Optional exact manifest path")
    args = parser.parse_args()

    config = normalize_config(read_json(CONFIG_PATH))
    layout = read_json(LAYOUT_PATH)
    channels = [item.strip() for item in args.channels.split(",") if item.strip()]
    channel_titles = parse_channel_titles(args.channel_title)
    template_id = args.template_id or config["default_template_id"]
    output_root = Path(args.output_root or config["output_root"]).expanduser().resolve()
    output_dir = output_root / args.run_id

    manifest = {
        "manifest_version": "v1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": args.run_id,
        "content_id": args.content_id or args.run_id,
        "skill": "social-media-cover",
        "template_id": template_id,
        "output_root": str(output_root),
        "output_dir": str(output_dir),
        "palette_lock": config["palette_lock"],
        "fonts": config["fonts"],
        "channels": {},
        "source": {
            "script_file": str(Path(args.script_file).resolve()) if args.script_file else None,
            "script_sha256": sha256_text(Path(args.script_file).read_text(encoding="utf-8")) if args.script_file else None
        },
        "policy": {
            "template_locked": True,
            "palette_locked": True,
            "output_root_locked": True,
            "font_locked": True,
            "text_color_override_allowed": bool(config["palette_lock"].get("allow_auto_text_color_change"))
        }
    }

    for channel in channels:
        if channel not in config["channels"]:
            raise SystemExit(f"Unknown channel: {channel}")
        if channel not in layout["platforms"]:
            raise SystemExit(f"Channel missing from layout_contract.json: {channel}")
        title_info = channel_titles.get(channel, {"main_title": "", "sub_title": ""})
        platform_layout = layout["platforms"][channel]
        manifest["channels"][channel] = {
            "platform": channel,
            "size": config["channels"][channel]["size"],
            "aspect": config["channels"][channel]["aspect"],
            "main_title": title_info["main_title"],
            "sub_title": title_info["sub_title"],
            "title_bbox": platform_layout["title"],
            "subtitle_bbox": platform_layout["subtitle"],
            "title_safe_zone": config["channels"][channel]["title_safe_zone"],
            "title_safe_zone_quality": config["channels"][channel]["title_safe_zone_quality"]
        }

    manifest_path = Path(args.out).resolve() if args.out else output_dir / "run_manifest.lock.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"manifest": str(manifest_path), "output_dir": str(output_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
