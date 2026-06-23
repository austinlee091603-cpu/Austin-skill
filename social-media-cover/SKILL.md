---
name: social-media-cover
description: Generate locked-layout social media covers from scripts and title candidates. Use when the user wants Douyin 3:4 or WeChat 21:9 cover images with account-style Chinese title extraction, a fixed virtual avatar IP, image2 textless backgrounds, crisp Pillow/Freetype final text compositing, optional HTML/CSS preview, sidecar JSON, QA, and trace output.
---

# Social Media Cover

Use this skill to turn a full script or article plus optional title candidates into final social media cover PNGs. The system must separate creative generation from deterministic layout:

- LLM: extracts theme, hook, content type, title candidates, avatar action, expression, outfit, props, scene, resolves the semantic task object, and writes `sidecar.json`.
- Visual Object Resolver: maps the script to a semantic frame, primary task object, allowed visual objects, and misread/forbidden objects before image2 prompting.
- image2: generates the real textless cover art, including the avatar integrated into the scene. It must not generate readable Chinese title text.
- pipeline: `scripts/run_cover_pipeline.py` is the only final delivery entry. It locks assets in `run_manifest.lock.json`, renders with Pillow, runs blocking QA, and writes `pipeline_report.json`.
- compositor: renders the final main title and subtitle as a locked title package with fixed coordinates, typography, platform-specific readability effects, and a theme-matched safe zone. Pillow/Freetype is the final renderer. HTML/CSS is preview-only and never a fallback delivery path.
- QA: checks length, text consistency, output size, title coordinates, avatar/title separation, semantic object lock, no obvious random text, and trace completeness. A run is not deliverable without a passing `qa_report.json` and `pipeline_report.json`.

## Inputs

Ask for or infer these inputs:

- Full script or WeChat article text.
- User title candidates, if available.
- Target platform: `douyin`, `wechat`, or both. If missing, ask before generating.
- Avatar reference image or locked avatar profile. On the user's first run, ask for a personal image reference before generating: real photo, multi-view avatar sheet, cartoon avatar, 3D avatar, or illustration-style virtual persona. After the first successful run, reuse the first locked avatar reference by default unless the user explicitly uploads or requests a new avatar.
- Optional template id: `black_yellow_punch`, `blue_black_tech`, or `white_clean_structure`.

## Non-Negotiable Preflight

Run these checks before planning or rendering:

1. Resolve the locked avatar reference. Prefer a user-supplied path, then `avatar_bible.json.default_reference_image`, then the newest successful `output/social-media-cover/*/*sidecar*.json` with `avatar.reference_image`, `avatar.locked_traits`, or `trace.locked_avatar_source`.
2. If a locked avatar exists, reuse it by default. Do not ask again, do not create a random person, and do not substitute a generic avatar unless the user explicitly changes identity.
3. If no locked avatar can be resolved, stop and ask for an avatar reference. Do not generate a deliverable cover.
4. If image2/textless background generation fails or is unavailable, stop and report the blocker. Do not silently use a placeholder, flat template, hand-drawn figure, or MVP fallback as final output.
5. There is no renderer MVP path for this skill. Delivery must use a planned sidecar plus a real textless background generated from the locked avatar and content metaphor.
6. Resolve a `visual_object_resolver` object before image2 prompting. It must include `semantic_frame`, `task_object`, `primary_visual_object`, `visual_metaphor`, `allowed_objects`, `forbidden_objects`, `misread_risks`, and `prompt_object_rules`. If it is missing or generic, stop and repair the sidecar before generating a background.
7. Use locked assets from `config/global_defaults.json` and `avatar_bible.json`: output root, template, palette, font paths, and default avatar reference. If any locked asset is missing, stop instead of falling back.
8. Final delivery must run through `scripts/run_cover_pipeline.py`. Do not call renderers directly for delivery.
9. Stop if the output directory is outside the configured `config/global_defaults.json.output_root/<run_id>/` unless the user explicitly overrides the output root in the current request.

## User Activation Flow

1. User provides a script/article.
2. Resolve the locked avatar via **Non-Negotiable Preflight**. Ask for a personal avatar reference only if no locked avatar or saved profile exists.
3. Ask or infer the output channel: `douyin`, `wechat`, or both. Do not silently assume when the requested channel is ambiguous.
4. Internally translate the script into title strategy, content type, and a semantic task object using `visual_object_taxonomy.json`. Do not jump directly from keywords to props.
5. Resolve the Visual Object Resolver: `semantic_frame`, `task_object`, `primary_visual_object`, `visual_metaphor`, `allowed_objects`, `forbidden_objects`, `misread_risks`, and `prompt_object_rules`.
6. Use the resolver to choose scene metaphor, avatar action/expression, prop, and image2 textless background prompt. Props must come from the resolver's allowed objects, and high-risk misread objects must appear in the negative prompt.
7. If both Douyin/Xiaohongshu and WeChat are requested from one script, create independent channel title pairs and background compositions, but keep the same locked `template_id`, palette, font family, output root, and semantic task object unless the platform truly needs a different composition of the same object.
8. Generate textless image2 background candidates using the locked avatar reference and content-specific action. Do not paste or crop the avatar manually. Do not proceed with a candidate whose avatar identity, semantic object, or title-safe zone is visibly wrong.
9. Save one approved textless background per platform as a real PNG. If no candidate is approved, stop and regenerate image2 backgrounds; do not use a placeholder.
10. Run `scripts/run_cover_pipeline.py` with the planned sidecar(s) and approved background(s). This creates `run_manifest.lock.json`, renders with Pillow, runs blocking QA, and writes `pipeline_report.json`.
11. If pipeline QA fails, stop or repair the specific failed branch. Do not claim delivery without `pipeline_report.json` showing `passed: true`.
12. Output final PNG, sidecar JSON, trace JSON, `run_manifest.lock.json`, platform `qa_report.json`, and `pipeline_report.json`.

## Workflow

1. Read `locked_visual_preamble.md`, `layout_contract.json`, `title_extraction_rules.md`, `avatar_bible.json`, `content_action_mapping.json`, `visual_object_taxonomy.json`, and `template_registry.json`.
2. Use `prompts/cover_planner.md` to extract content strategy, resolve the visual task object, and generate a sidecar draft.
3. Use `prompts/title_normalizer.md` to generate account-style cover titles. Default Douyin mode allows `main_title <= 8` Chinese characters and `sub_title <= 12` Chinese characters. WeChat editorial mode allows `main_title <= 10` Chinese characters and `sub_title <= 16` Chinese characters. Compact punch mode can still use shorter 3-5 character poster words only when the content genuinely calls for it. Never resize text outside locked variants.
4. Validate the draft against `sidecar_schema.json`.
5. Use `prompts/image2_background_prompt.md` to generate approved `background.png` candidates for each platform from `visual_object_resolver`. Keep the title area clean, dark, low-detail, textless, and free of large panels/frames/glow fields that compete with the compositor text.
6. Run `scripts/run_cover_pipeline.py` as the only final delivery path. It creates the manifest, copies locked backgrounds into the run folder, renders final covers with Pillow, and runs `scripts/qa_cover.py`.
7. Preserve trace output and QA reports. QA failures are blocking.

## Output Directory

Default all generated covers under the locked global output root:

```text
./output/social-media-cover/<run_id>/
```

Use a short content-based `<run_id>` such as `nvidia_alpamayo`, `lixiang_ai`, or `jiyue_restructure`. Do not create new sibling folders like `output/social-media-cover_nvidia_alpamayo`; keep every run inside the configured output root.

## Hard Rules

- Main title and subtitle are one line only.
- Default title color is locked to `#FFD61E`; default subtitle color is locked to `#FFFFFF`. Do not change text colors automatically for any platform. If contrast fails, repair or regenerate the background/title-safe zone, or apply an approved deterministic readability layer; do not switch to blue/white, cyan, or another template palette unless the user explicitly asks for that color change.
- Default template is locked to `black_yellow_punch` for all platforms. For one script generating multiple platforms, do not switch WeChat to `blue_black_tech` or another template unless the user explicitly asks for a different WeChat style.
- Default Douyin account-title mode: main title max length 8 Chinese characters, subtitle max length 12 Chinese characters.
- WeChat editorial-title mode: main title max length 10 Chinese characters, subtitle max length 16 Chinese characters. WeChat should usually carry more explanatory text than Douyin because the canvas is horizontal and the left title zone is wider.
- Compact punch-title mode: main title max length 5 Chinese characters, subtitle max length 8 Chinese characters.
- Choose account-title mode unless the user explicitly wants ultra-short poster words or the script naturally calls for a 3-5 character label.
- Text position, font size, font weight, stroke, shadow, alignment, and line height are locked in `layout_contract.json`.
- Default Douyin/Xiaohongshu vertical covers must use no title/subtitle stroke and no shadow. Solve readability through the image2 quiet title buffer and background contrast planning, not black compositor effects.
- When a title/subtitle has `stroke_width: 0` and `shadow: false`, the Pillow renderer must draw that text once only. Do not apply synthetic offset redraws, fake bold layers, blur, or shadow-like duplicate passes because they soften Chinese glyph edges.
- The Douyin title/subtitle group is locked to the current visual position by equal top/bottom visual margins inside the title-safe zone, but the compositor must not force a visible hard frame behind it. The background prompt must create a quiet title buffer with low-contrast texture and weak edges.
- WeChat 21:9 uses an independent left-mid editorial title system: the title group is vertically centered, left aligned, longer than Douyin when useful, and styled with light or no stroke/shadow because the background is planned for readability first.
- Overflow policy is always `rewrite_text_not_resize`.
- image2 must not render final readable title text.
- Every sidecar must include `visual_object_resolver`. It is the source of truth for the semantic task object and visual object whitelist/blacklist.
- Do not turn generic words like "card", "cover", "result", "panel", "screen", or "output" into props before resolving the task object. These words are high-risk because they can become phones, tablets, app screens, or product slabs.
- If the resolver says the topic is an open-source skill/workflow release, prioritize repository gates, source-code boxes/vaults, workflow engines, script-to-output pipelines, layout locks, and poster layout sheets. Forbid phones, tablets, hardware product launches, glossy black slabs, and app-device showcases.
- Cover outputs should look like flat poster/layout sheets, paper thumbnails, wall thumbnails, or locked composition frames. They must not look like handheld phones or tablets unless the script is actually about mobile devices.
- The title-safe zone is content-derived, not a fixed visual module. It may be UI glass, sky blank, glow field, cockpit window, courtroom light box, shield glow, product light panel, or another clean theme-native area. It must read as breathing room in the scene, not as a pasted rectangular title container.
- The title-safe zone must remain dark/low-detail enough for the locked yellow/white text. For Douyin/Xiaohongshu, do not allow a yellow or warm glow wash behind the title. For WeChat, do not allow a large glass panel, UI frame, border, or visible title container around the left title area.
- Dark title-safe zones must not become pure black, dead black, or oppressive black-gold voids. Prefer a breathable blue-black technology space: deep navy/cobalt ambient light, faint scene-native blue glow, subtle low-contrast tech lines, and enough atmospheric depth to connect the title zone to the rest of the cover while preserving yellow/white text readability.
- For WeChat covers, the left side remains the title zone but must not be pure blank. image2 should generate subtle article-derived background elements there, such as skill-tree nodes, workflow cards, light paths, data grids, cockpit/window glow, legal papers, product diagrams, shield glows, or other low-contrast metaphors that support the article while preserving title readability.
- For WeChat covers, the left title zone should feel decorated-but-readable, not empty: use low-contrast workflow nodes, circuit outlines, soft grid-floor perspective, dim blue light paths, tiny data/cube particles, ghosted document cards, or weak card silhouettes. These elements must come from image2, remain subtle, and must not create a large title frame, UI panel, or readable labels.
- The compositor must not add random decorative left-side elements after the fact; left-side context elements should come from the image2 textless background plan.
- Avoid rigid hard-edged title frames. If a frame exists, weaken the edges so the title remains the first-read subject.
- The avatar is an emotional actor. It must participate in the visual metaphor through pose, expression, prop, or interaction.
- The avatar must not be manually cut out and pasted as the final background. Use image2 to regenerate the avatar from the reference traits.
- First-run avatar locking: once the user provides the first avatar reference and a cover is generated, use that avatar identity as the default for later covers.
- Avatar updates only happen when the user provides a new avatar image or explicitly asks to change the locked avatar.
- The avatar must not reduce title readability.
- Placeholder backgrounds, flat geometric backgrounds, stick-figure avatars, manually drawn fallback personas, or MVP renderer fallbacks are never acceptable final outputs.
- Renderer, planner, image, font, template, color, or avatar fallbacks are not allowed for delivery. Missing assets are blockers.
- Output must include final PNG, sidecar JSON, trace JSON, `run_manifest.lock.json`, platform `qa_report.json`, and `pipeline_report.json`.
- Trace must record the actual final renderer, authoritative final PNG path, loaded title/subtitle font path, background source/hash, sidecar hash, and QA status.

## Final Delivery Command

From the skill folder or project root:

```bash
python3 ~/.codex/skills/social-media-cover/scripts/run_cover_pipeline.py \
  --run-id <run_id> \
  --channels douyin,wechat \
  --script-file /path/to/script.txt \
  --sidecar douyin:/path/to/douyin_sidecar.json \
  --sidecar wechat:/path/to/wechat_sidecar.json \
  --background douyin:/path/to/douyin_background.png \
  --background wechat:/path/to/wechat_background.png
```

HTML/CSS preview is optional and preview-only:

```bash
node ~/.codex/skills/social-media-cover/render/render_cover.ts \
  --sidecar /path/to/sidecar.json \
  --background /path/to/background.png \
  --platform douyin \
  --out output/social-media-cover/<run_id>
```

## Expected Outputs

Each platform writes:

- `{platform}_final_pillow.png` as the preferred authoritative final image when Pillow/Freetype rendering is used.
- `{platform}_final.png` only as optional HTML/CSS preview.
- `{platform}_sidecar.json`
- `{platform}_trace.json`
- `{platform}_qa_report.json`
- `run_manifest.lock.json`
- `pipeline_report.json`

When image2 is used, keep `{platform}_background.png` beside the final output for audit.
