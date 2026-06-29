# Austin Skills

This is a collection of Codex Skills. Each top-level folder is an independent skill that can be copied into `~/.codex/skills/`.

Currently included:

- `social-media-cover`: Generates Douyin/Xiaohongshu 3:4 vertical covers, Douyin/Xiaohongshu 4:3 landscape covers, and WeChat official account 21:9 covers from scripts or articles. When you ask for a Douyin/Xiaohongshu cover without specifying a ratio, the skill outputs both 3:4 and 4:3 by default. The workflow uses a fixed real-person or virtual avatar as the creator IP: upload it once on the first run, and later runs reuse it by default unless you explicitly upload a new image. By default, the skill calls the image2 model to generate textless backgrounds, extracts suitable main/subtitle text from the script or article, and then uses Pillow to render the final text layer so text color, position, and channel rules stay consistent. A QA pass is run at the end.

Note: this skill is only intended for Codex.

[中文](README.md)

## Installation

Install one skill:

```bash
mkdir -p ~/.codex/skills
cp -R social-media-cover ~/.codex/skills/social-media-cover
```

If you cloned the whole repository, run this from the repository root:

```bash
mkdir -p ~/.codex/skills
cp -R ./social-media-cover ~/.codex/skills/social-media-cover
```

The public version does not include private avatars, private fonts, or generated outputs. Read the skill-level README before using a skill and provide any required local assets.

## Activation

Mention the skill in Codex:

```text
Use $social-media-cover to generate Douyin/Xiaohongshu covers and a WeChat 21:9 cover from this script. By default, Douyin/Xiaohongshu outputs both 3:4 vertical and 4:3 landscape covers. You can also request one ratio or only the WeChat cover.
```

## Best For

- Turning repeatable content-production workflows into reusable Codex skills.
- Producing consistent covers for creator accounts, WeChat articles, and short-video platforms.
- Letting AI handle content understanding and background generation while rules lock layout, typography, color, QA, and reproducibility.
- Creator accounts that need long-term avatar identity consistency.

## Not For

- A plug-and-play template library with no local asset configuration.
- Fully random visual ideation on every run.
- Asking the image model to draw final readable Chinese titles.
- Placeholder delivery when backgrounds or QA fail.

## Repository Layout

```text
.
├── README.md
├── README.en.md
├── LICENSE
├── .gitignore
└── social-media-cover/
    ├── SKILL.md
    ├── README.md
    ├── README.en.md
    ├── config/
    ├── prompts/
    ├── render/
    ├── scripts/
    ├── tests/
    ├── assets/
    └── examples/
```

## Open Source Notes

This repository should contain skill rules, scripts, templates, examples, and placeholder asset instructions only. Do not commit private avatar images, commercial fonts, generated outputs, or personal local paths.
