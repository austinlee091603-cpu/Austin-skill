# Hash Traceability

Every render should emit a trace JSON containing:

- `created_at`
- `platform`
- `content_id`
- `template_id`
- `layout_contract_version`
- `render_version`
- `renderer`
- `run_manifest.lock.json` path and SHA-256 hash when present
- `config/global_defaults.json` SHA-256 hash
- locked text color values: `title_fill`, `subtitle_fill`, and `allow_auto_text_color_change`
- final text font path and font family/name for title and subtitle
- SHA-256 hash of sidecar content
- SHA-256 hash of layout contract
- SHA-256 hash of template registry
- SHA-256 hash of background image when provided
- image2/generated background source path when available
- authoritative output PNG path. If `{platform}_final_pillow.png` exists, it is the final deliverable; `{platform}_final.png` is only an optional preview.
- sidecar JSON path
- trace JSON path
- QA results

Trace exists so covers can be reproduced, compared, audited, and A/B tested.

## Required QA Evidence

- The final title and subtitle in trace must match sidecar text.
- `font.title_font_path` and `font.subtitle_font_path` must record the actual font loaded by the renderer. For the current locked Chinese style, prefer `./assets/fonts/title-font.ttf`.
- `output.final_png` must point to the authoritative final file, not an old preview or chat thumbnail.
- Background source should be preserved enough to audit image2 output versus compositor output.
- Text colors in trace must match `run_manifest.lock.json` / `config/global_defaults.json`. The default locked values are title `#FFD61E` and subtitle `#FFFFFF`.
- Any `qa_report.json` failure is blocking; do not deliver a final cover while QA is failing.
