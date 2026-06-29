#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


SKILL_DIR = Path(__file__).resolve().parents[1]
QA_SCRIPT = SKILL_DIR / "scripts" / "qa_cover.py"


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_manifest(root: Path):
    return {
        "manifest_version": "test",
        "run_id": "regression",
        "template_id": "black_yellow_punch",
        "output_root": str(root),
        "output_dir": str(root / "regression"),
        "palette_lock": {
            "title_fill": "#FFD61E",
            "subtitle_fill": "#FFFFFF",
            "allow_auto_text_color_change": False
        },
        "fonts": {
            "title_font_path": "./assets/fonts/title-font.ttf",
            "subtitle_font_path": "./assets/fonts/title-font.ttf",
            "allow_font_fallback": False
        },
        "channels": {
            "douyin": {
                "size": [1080, 1440],
                "title_bbox": {"max_chars": 8},
                "subtitle_bbox": {"max_chars": 12},
                "title_safe_zone": {"x": 0, "y": 0, "width": 1080, "height": 420},
                "title_safe_zone_quality": {
                    "max_mean_luma": 105,
                    "max_yellow_pixel_ratio": 0.08,
                    "max_edge_density": 0.17,
                    "max_border_edge_ratio": 0.34
                }
            },
            "wechat": {
                "size": [1260, 540],
                "title_bbox": {"max_chars": 10},
                "subtitle_bbox": {"max_chars": 16},
                "title_safe_zone": {"x": 0, "y": 0, "width": 630, "height": 540},
                "title_safe_zone_quality": {
                    "max_mean_luma": 95,
                    "max_yellow_pixel_ratio": 0.06,
                    "max_edge_density": 0.15,
                    "max_border_edge_ratio": 0.30,
                    "ignore_canvas_outer_edges": True
                }
            }
        }
    }


def base_files(root: Path, platform: str, palette=None, final_outside_root=False):
    out = root / "regression"
    out.mkdir(parents=True, exist_ok=True)
    size = (1080, 1440) if platform == "douyin" else (1260, 540)
    bg = Image.new("RGB", size, (8, 14, 20))
    background = out / f"{platform}_background.png"
    final = (root.parent / "outside.png") if final_outside_root else out / f"{platform}_final_pillow.png"
    bg.save(background)
    bg.save(final)
    sidecar = {
        "content_id": "regression",
        "platform": platform,
        "template_id": "black_yellow_punch",
        "main_title": "封面Skill" if platform == "douyin" else "封面Skill开源",
        "sub_title": "我把它开源了" if platform == "douyin" else "脚本到成片工作流",
        "visual_object_resolver": {
            "semantic_frame": "open_source_workflow_release",
            "task_object": "Codex cover skill repository and reusable script-to-cover workflow",
            "primary_visual_object": "repository source-code workflow engine",
            "visual_metaphor": "a repository gate unlocks a source-code workflow engine",
            "allowed_objects": ["repository gate", "source-code box", "workflow engine", "flat poster layout sheets"],
            "forbidden_objects": ["phone", "tablet", "hardware product", "black glass slab"],
            "misread_risks": ["poster sheets may look like phone slabs if rendered as glossy black rectangles"],
            "prompt_object_rules": {
                "must_include": ["repository", "source-code", "workflow engine"],
                "must_exclude": ["phone", "tablet", "hardware product", "black glass slab"]
            },
            "semantic_qa": {
                "first_read_should_be": "open-source cover skill workflow release",
                "must_not_read_as": "phone or tablet product launch",
                "manual_check_required": True
            }
        },
        "image_prompt": {
            "background_prompt": "repository source-code workflow engine with flat poster layout sheets",
            "negative_prompt": "phone, tablet, hardware product, black glass slab"
        },
        "constraints": {
            "semantic_object_lock": True
        }
    }
    if platform == "wechat":
        sidecar["constraints"].update({
            "left_50_text_zone": True,
            "right_50_visual_zone": True,
            "soft_transition_band": True,
            "no_text_cross_50_percent_boundary": True
        })
    trace_palette = palette or {"title_fill": "#FFD61E", "subtitle_fill": "#FFFFFF"}
    trace = {
        "platform": platform,
        "template_id": "black_yellow_punch",
        "text_color": trace_palette,
        "font": {
            "title_font_path": "./assets/fonts/title-font.ttf",
            "subtitle_font_path": "./assets/fonts/title-font.ttf"
        },
        "rendered_text": {
            "title_bbox": {"x": 72, "y": 205, "width": 420, "height": 70, "right": 492, "bottom": 275},
            "subtitle_bbox": {"x": 78, "y": 292, "width": 360, "height": 40, "right": 438, "bottom": 332}
        }
    }
    sidecar_path = out / f"{platform}_sidecar.json"
    trace_path = out / f"{platform}_trace_pillow.json"
    write_json(sidecar_path, sidecar)
    write_json(trace_path, trace)
    return background, final, sidecar_path, trace_path


def run_case(name: str, platform: str, manifest: Path, background: Path, final: Path, sidecar: Path, trace: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(QA_SCRIPT),
            "--manifest",
            str(manifest),
            "--sidecar",
            str(sidecar),
            "--trace",
            str(trace),
            "--background",
            str(background),
            "--final",
            str(final),
            "--platform",
            platform,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return {"case": name, "failed_as_expected": result.returncode != 0, "returncode": result.returncode}


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "output" / "social-media-cover"
        manifest_path = root / "regression" / "run_manifest.lock.json"
        write_json(manifest_path, make_manifest(root))

        results = []

        bg, final, sidecar, trace = base_files(root, "douyin")
        Image.new("RGB", (1080, 1440), (235, 184, 18)).save(bg)
        Image.open(bg).save(final)
        results.append(run_case("douyin_yellow_title_glow_fails", "douyin", manifest_path, bg, final, sidecar, trace))

        bg, final, sidecar, trace = base_files(root, "wechat")
        frame = Image.new("RGB", (1260, 540), (8, 14, 20))
        draw = ImageDraw.Draw(frame)
        draw.rectangle((0, 0, 630, 539), outline=(120, 180, 230), width=10)
        frame.save(bg)
        frame.save(final)
        results.append(run_case("wechat_large_left_frame_fails", "wechat", manifest_path, bg, final, sidecar, trace))

        bg, final, sidecar, trace = base_files(root, "wechat")
        trace_data = json.loads(trace.read_text(encoding="utf-8"))
        trace_data["rendered_text"]["title_bbox"]["right"] = 655
        write_json(trace, trace_data)
        results.append(run_case("wechat_text_cross_50_percent_boundary_fails", "wechat", manifest_path, bg, final, sidecar, trace))

        bg, final, sidecar, trace = base_files(root, "wechat", palette={"title_fill": "#F5FBFF", "subtitle_fill": "#6FE7FF"})
        results.append(run_case("wechat_blue_palette_drift_fails", "wechat", manifest_path, bg, final, sidecar, trace))

        bg, final, sidecar, trace = base_files(root, "douyin", final_outside_root=True)
        results.append(run_case("output_root_drift_fails", "douyin", manifest_path, bg, final, sidecar, trace))

        bg, final, sidecar, trace = base_files(root, "douyin")
        broken = json.loads(sidecar.read_text(encoding="utf-8"))
        broken.pop("visual_object_resolver", None)
        write_json(sidecar, broken)
        results.append(run_case("missing_visual_object_resolver_fails", "douyin", manifest_path, bg, final, sidecar, trace))

        passed = all(item["failed_as_expected"] for item in results)
        print(json.dumps({"passed": passed, "results": results}, ensure_ascii=False, indent=2))
        if not passed:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
