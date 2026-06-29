# Social Media Cover Skill

This skill turns a full script or article into stable social media cover images for short-video platforms and WeChat official account articles. It separates creative generation from deterministic production:

1. Read the full script/article and extract the theme, pain point, conflict, content type, and title strategy.
2. Lock the personal avatar identity and plan the avatar action, expression, prop, and scene interaction.
3. Generate a real textless background with image2.
4. Render the main title and subtitle with Pillow/Freetype using locked layout rules.
5. Output the final PNG, sidecar, trace, manifest, QA report, and pipeline report.

## Installation

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R social-media-cover ~/.codex/skills/social-media-cover
```

The public version does not include private avatar or font assets. Before the first run, provide:

- `assets/avatar/reference-avatar.png`: your locked personal avatar reference.
- `assets/fonts/title-font.ttf`: the Chinese title font used by the Pillow renderer.

You can also edit `config/global_defaults.json` and `avatar_bible.json` to point to different explicit paths. If the avatar or font is missing, the pipeline fails instead of falling back.

## Activation

In Codex, use:

```text
Use $social-media-cover to generate Douyin/Xiaohongshu covers and a WeChat 21:9 cover from this script.
```

Or request a single channel:

```text
Use $social-media-cover to generate a WeChat cover.
```

## Best For

- Douyin/Xiaohongshu 3:4 vertical covers.
- Douyin/Xiaohongshu 4:3 landscape covers, bundled with the 3:4 vertical cover by default.
- WeChat official account 21:9 covers.
- Creator accounts with a consistent avatar IP.
- Cover title extraction from a full script or article.
- Long-term consistency in layout, title color, font, and avatar identity.

## Not For

- Final covers without an avatar reference.
- Placeholder-template generation when image2 background generation is unavailable.
- Asking the image model to draw final readable Chinese title text.
- Fully random visual exploration with different personas and layouts each time.

## Output

Default run output:

```text
./output/social-media-cover/<run_id>/
```

Each platform writes:

- `{platform}_background.png`
- `{platform}_final_pillow.png`
- `{platform}_sidecar_pillow.json`
- `{platform}_trace_pillow.json`
- `{platform}_qa_report.json`
- `run_manifest.lock.json`
- `pipeline_report.json`

## Principle

AI handles content understanding, visual planning, and textless background generation. Rules handle title length, layout, color, font, avatar locking, and QA. Missing assets, failed backgrounds, or failed QA are blockers, not reasons to use fallback output.
