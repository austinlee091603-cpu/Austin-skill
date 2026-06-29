# QA Checker Prompt

Review the sidecar, layout contract, background, final PNG, and trace.

## Required Checks

1. `main_title.length <= layout_contract.title.max_chars`.
2. `sub_title.length <= layout_contract.subtitle.max_chars`.
3. Rendered title text equals sidecar title text.
4. Rendered subtitle text equals sidecar subtitle text.
5. Title and subtitle coordinates match `layout_contract.json`.
5.1. If Pillow output exists, `{platform}_final_pillow.png` is the authoritative final preview/delivery image; do not QA or show an older `{platform}_final.png` as final.
6. Title and subtitle are one line only.
7. No font auto-scaling occurred.
8. Avatar does not overlap the title area.
9. Avatar scale does not exceed platform max.
10. Avatar action/expression matches the script and is not a lazy repeat of the prior cover action unless justified.
10.1. Avatar identity matches the locked avatar reference or locked traits from `avatar_bible.json` / prior sidecar; reject generic people, flat placeholders, stick figures, or missing-avatar MVP output.
10.2. Sidecar includes `visual_object_resolver` with a non-generic semantic frame, task object, primary visual object, allowed objects, forbidden objects, misread risks, prompt object rules, and semantic QA notes.
10.3. The image prompt is derived from `visual_object_resolver`: positive prompt includes the primary visual object and must-include terms; negative prompt includes forbidden/misread objects and must-exclude terms.
10.4. The first-read visual object must match `visual_object_resolver.task_object`. Reject a cover that reads as another product category, business category, or hardware launch even if title and technical QA pass.
10.5. If the resolver flags a misread risk, inspect the generated background for that risk. Example: open-source workflow release covers must not look like phone/tablet/app-device product launches.
11. No decorative line, UI accent, or background element collides with the first title character.
12. Final title and subtitle are visually crisp at 100% size, not fuzzy, pixelated, or eaten by stroke.
12.1. Trace records the actual loaded title/subtitle font path and font name. For the locked Chinese title style, verify it uses the configured Jinghua Old Song font when available.
13. Title-zone background must not contain a hard black fill block, obvious pasted rectangular title box, or visible forced frame edge unless it is a weak scene-native object.
14. Title/subtitle group should be vertically centered inside the visible title zone: distance from main-title top to title-zone top should visually match distance from subtitle bottom to title-zone bottom.
14.1. The title-safe zone may be a UI frame, sky blank, glow field, cockpit window, courtroom light box, shield glow, product light panel, or other content-derived clean area. It must not default to the same rigid hard-edged frame across all covers.
14.2. Any frame edges must be weak/subtle enough to support readability without becoming the visual subject.
14.3. For WeChat 21:9 covers, the title group should be vertically centered on the canvas, left aligned, and use the WeChat editorial title scale from `layout_contract.json`.
14.4. For WeChat 21:9 covers, the left title side should not be empty blank space. It should contain subtle article-derived visual elements generated in the image2 background, while keeping the title readable.
14.5. For WeChat 21:9 covers, reject random compositor-added decorative elements on the left side unless explicitly marked as a temporary manual adjustment.
14.6. For WeChat 21:9 covers, reject heavy black stroke or heavy black shadow. Default WeChat text should use no stroke/shadow because the background must be prepared for readability.
14.7. For Douyin/Xiaohongshu covers, the title-safe zone should be background-generated breathing room, not a compositor-forced hard frame.
14.8. For Douyin/Xiaohongshu covers, reject any default title/subtitle stroke, shadow, CSS text-shadow, synthetic offset redraw, or forced dark title backing. The layout contract should specify `stroke_width: 0` and `shadow: false` for both title fields.
14.9. For Douyin/Xiaohongshu 4:3 landscape covers, reject any background or final cover that looks mechanically cropped from the 3:4 vertical cover, stretched from another platform, stitched from separate sections, split into obvious left/right panels, or laid out like a WeChat banner.
14.10. For Douyin/Xiaohongshu 4:3 landscape covers, verify the title uses the same centered top title principle as the vertical cover. Reject default upper-left or left-title/right-visual layouts.
14.11. For Douyin/Xiaohongshu 4:3 landscape covers, reject top title zones invaded by avatar face, bright nodes, gold props, clocks, radars, app bubbles, product objects, high-contrast workflow lines, or any strong object that competes with the title.
14.12. For Douyin/Xiaohongshu 4:3 landscape covers, verify the avatar and primary metaphor live below the title zone and that the avatar participates in the script-specific action rather than becoming a corner sticker.
14.13. For Douyin/Xiaohongshu 3:4 plus 4:3 bundled covers, verify the two outputs share identity, palette, typography, semantic object, and visual mother-theme, but do not use the exact same background crop or identical avatar action/expression.
14.14. For Douyin/Xiaohongshu 4:3 landscape covers, verify the title wording follows `landscape_account_explainer`: main title <= 10 Chinese characters and subtitle <= 15 Chinese characters, retaining short-video impact rather than becoming a WeChat editorial headline.
14.15. For WeChat covers, verify the title and subtitle rendered bounding boxes are fully inside the left 50% of the canvas. Reject text that crosses into the right visual half even if the character count passes.
14.16. For WeChat covers, verify the right 50% contains the avatar, main content-derived visual object, and interaction action; the left 50% should contain only quiet low-detail context.
14.17. For WeChat covers, reject visible vertical seams, hard cuts, blur walls, pasted split panels, strong objects crossing the 50% boundary into the title text, or high-contrast divider-like elements.
15. Background has no obvious random readable Chinese text, English letters, numbers, labels, or typography-like glyphs.
16. Final PNG size equals platform spec.
17. Trace includes hashes, template id, platform, content id, output path, and QA results.
18. Trace output path must point to the authoritative final PNG. If Pillow rendering is used, this should be `{platform}_final_pillow.png`.
19. Final delivery uses no fallback path. If trace or sidecar says `mvp_heuristic_sidecar`, `allow_mvp_fallback`, `image2_background_used: false`, or no real background path/hash is present, reject.
20. Final output path is under `./output/social-media-cover/<run_id>/`.
21. `template_id` matches `run_manifest.lock.json`; default locked template is `black_yellow_punch`.
22. Trace text colors match the manifest/global defaults: main title `#FFD61E`, subtitle `#FFFFFF`. Reject blue/cyan or platform-specific color drift unless the user explicitly requested it.
23. Trace font paths match the configured locked font paths. Reject silent fallback.
24. Title-safe-zone metrics from `scripts/qa_cover.py` pass: brightness, yellow saturation, edge density, and large-frame likelihood must be under configured thresholds.
25. For Douyin/Xiaohongshu, reject yellow glow or warm bright haze in the top title-safe zone.
26. For WeChat, reject a large glass panel, UI frame, title box, data panel, or visible rectangular container around the left title area.
27. For open-source skill/workflow release scripts, reject glossy black rectangles, handheld slabs, product lineups, or floating device-like outputs unless the script is actually about devices. Cover outputs should read as flat poster sheets, paper layouts, wall thumbnails, or layout frames.
28. For `douyin_xhs_landscape`, sidecar constraints should include `no_hard_crop: true`, `independent_horizontal_composition: true`, `center_top_title_system: true`, and `adversarial_review_complete: true`.
29. For `wechat`, sidecar constraints should include `left_50_text_zone: true`, `right_50_visual_zone: true`, `soft_transition_band: true`, and `no_text_cross_50_percent_boundary: true`.

## Output

Return JSON:

```json
{
  "passed": true,
  "failures": [],
  "warnings": [],
  "trace_complete": true
}
```
