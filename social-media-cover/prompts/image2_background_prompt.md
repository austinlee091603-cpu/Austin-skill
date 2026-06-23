# image2 Background Prompt Builder

Use this prompt to produce the real textless cover art for the compositor. This is not a placeholder step.

## Required Content

Include:

- Platform ratio and output size.
- Selected template mood and palette.
- User's fixed virtual avatar identity.
- Avatar reference image and locked traits.
- If this is not the first run, use the locked avatar reference/traits from prior sidecar trace unless the user provides a new avatar image.
- Avatar placement, pose, expression, and interaction with the scene.
- Content-related action, expression, outfit, prop, scene, and interaction object.
- `visual_object_resolver.semantic_frame`, `task_object`, `primary_visual_object`, `visual_metaphor`, `allowed_objects`, `forbidden_objects`, `misread_risks`, and `prompt_object_rules`.
- Prior cover's avatar action/expression, if available, so the next cover can avoid repeating the same pose.
- Clean title area requirement.
- A clear Douyin-cover visual story: one large metaphor, one expressive avatar action, one strong readable title-safe zone.
- For WeChat 21:9 covers, a left-side title-safe zone with subtle content-derived visual elements, not empty blank space.

## Must Say

- Do not render final readable Chinese title text.
- Do not render random Chinese words, watermarks, captions, interface labels, or typography-like glyphs.
- Leave the locked title zone dark, low-detail, and clean enough for later locked yellow/white compositor text. Do not use bright glow fills in the text bbox.
- Dark does not mean pure black. The locked title zone should usually be quiet dark-blue breathing room with deep navy/cobalt ambience, faint scene-native blue glow, and subtle atmospheric depth. Avoid pure black, dead black, oppressive black-gold, and charcoal-only voids.
- The title zone must exist as negative space, not as a visible title module. Do not create a large glass title panel, UI frame, data panel, title box, or rectangular container inside the title-safe bbox.
- Avoid rigid, solid, hard-edged black rectangles, obvious pasted rectangular title boxes, large frames, and visible panel borders.
- The title-safe zone should be generated from the script's metaphor and scene logic, not copied as the same module across every cover.
- For Douyin/Xiaohongshu, reserve a center-top readability buffer through quiet dark-blue breathing room, deep navy/cobalt ambient light, subtle blue volumetric glow, faint low-contrast tech lines, and depth blur. Do not use pure black/dead black, yellow glow, warm glow, bright haze, glass panel, UI card, or data panel behind the future title group.
- For WeChat covers, the left title-safe zone should remain readable but not visually empty. Add only faint, low-contrast article-derived elements integrated into the background, such as tiny workflow-node traces, very dim light paths, or soft data-grid texture. These elements must not form a large frame or panel around the title.
- For WeChat covers, the left title-safe zone must be decorated-but-readable, not blank. Use low-contrast workflow nodes, circuit outlines, soft grid-floor perspective, dim blue light paths, tiny cube/data particles, ghosted document cards, or weak card silhouettes. These elements must remain background texture only, connect naturally into the right-side scene, and never compete with future yellow/white title text.
- For WeChat covers, make the left title side readable enough for the compositor to use no text stroke and no shadow by default. Avoid bright objects behind the future title text.
- The avatar must be integrated into the scene by image2, not pasted in later.
- Treat the locked avatar reference as identity input for image2. Preserve stable identity traits while changing only action, expression, outfit variation, prop, and scene relationship.
- Do not default to the same pose across covers. If the prior cover used pointing upward, pressing a button, or facing front, choose a different content-specific pose unless the script explicitly requires it.
- Avatar action must be selected from the script's semantic role, not from a generic "point to title" template.
- The avatar may be medium-small or medium size if it performs an action and supports the hook; avoid lifeless corner stickers and avoid extreme big-head close-ups.
- Use props and background that come from the script meaning, not generic decoration.
- Use only props and object language supported by `visual_object_resolver.allowed_objects`. Do not introduce visual objects because they are common in thumbnails.
- Do not use ambiguous object words such as card, slab, screen, panel, output, result, or device unless they are explicitly disambiguated by the resolver. When the topic is cover production, prefer "flat poster layout sheet", "paper layout", "wall-mounted poster thumbnail", or "locked layout frame" over "card" or "screen".
- Copy every `prompt_object_rules.must_exclude` term into the negative prompt, and make the positive prompt visibly include the `primary_visual_object`.
- If `semantic_frame` is `open_source_workflow_release`, the image should first read as a repository/source-code/workflow release: repository gate, source-code vault or box, workflow engine, script-to-output pipeline, layout lock layer. It must not read as a phone/tablet/hardware/app launch.
- For Douyin, favor high-recognition visual metaphors like a courtroom pause button, protection shield, ICU/rescue metaphor, debt storm frozen in place, or rebirth gate, depending on the script.

## Prompt Template

Create a textless social media cover background for `{platform}` at `{width}x{height}`. Use the `{template_id}` visual mood: `{template_mood}`. Preserve the user's fixed virtual avatar identity from the reference image: `{avatar_identity}`. Regenerate the avatar naturally inside the scene, do not paste or crop the reference. The avatar should use `{avatar_expression}` expression and `{avatar_action}` action, wearing `{avatar_outfit}`, interacting with `{prop}` in a `{scene_type}` scene.

Semantic object lock: the selected frame is `{semantic_frame}`. The task object is `{task_object}`. The primary visual object is `{primary_visual_object}`. The visual metaphor is `{visual_metaphor}`. Use only these allowed object families: `{allowed_objects}`. Avoid these misread objects: `{forbidden_objects}`. Address these risks: `{misread_risks}`. The visual story should communicate `{core_hook}` and `{core_value}` through the locked task object, not through generic tech decoration.

Composition: reserve a strong clean center-top title zone for compositor text; the zone must be quiet dark-blue breathing room with enough contrast for locked yellow/white Chinese text, deep navy/cobalt ambience, faint scene-native blue glow, subtle low-contrast tech lines, and atmospheric depth. It must not be empty pure black, dead black, oppressive black-gold, or charcoal-only. Do not place yellow glow, warm glow, bright haze, a glass panel, UI card, data panel, title box, or visible rectangular frame inside the title-safe bbox. Arrange scene elements around and below it to create a bold Douyin thumbnail. Use an expressive avatar, strong depth, high contrast, and one obvious metaphor from the resolver. Avatar pose should be content-specific and visibly different from recent covers when possible. No final readable Chinese title text, no random Chinese words, no watermarks, no captions, no typography-like glyphs.

WeChat composition override: use 21:9 editorial composition. Reserve the left 42% as a readable dark-blue title-safe zone, with the title group expected around vertical center. The left zone must not be pure blank space or a plain dark rectangle. Add subtle background texture only: low-contrast workflow nodes, circuit outlines, soft grid-floor perspective, dim blue light paths, tiny cube/data particles, ghosted document cards, or weak card silhouettes. These details should connect naturally into the right-side scene while staying quiet behind the future title center. No large glass panel, no UI frame, no title box, no data panel, no visible border, and no bright/high-contrast objects behind the future title center. Put the avatar and stronger metaphor scene mainly on the right side or right third.

Negative prompt: readable Chinese text, random letters, numbers, Lv labels, watermark, subtitle, caption, logo text, cluttered title zone, pure black title zone, dead black background, oppressive black-gold-only palette, yellow glow behind title, warm glow wash behind title, large glass title panel, UI frame, data panel, title box, empty plain left title side for WeChat, hard solid black title block, thick rigid border, repeated identical title module, pasted cutout, low-resolution avatar, blurry face, flat geometric filler, meaningless yellow blocks, lifeless corner avatar, photoreal random person, inconsistent avatar identity, plus every item in `{forbidden_objects}` and `{prompt_object_rules.must_exclude}`.
