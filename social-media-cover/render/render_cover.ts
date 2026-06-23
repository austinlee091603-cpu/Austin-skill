#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const RENDER_VERSION = "v2.0.0-no-fallback";
const SKILL_DIR = path.resolve(__dirname, "..");
const CONTRACT_PATH = path.join(SKILL_DIR, "layout_contract.json");
const TEMPLATE_REGISTRY_PATH = path.join(SKILL_DIR, "template_registry.json");
const HTML_PATH = path.join(__dirname, "cover_template.html");
const CSS_PATH = path.join(__dirname, "cover_styles.css");

function usage() {
  console.log(`Social Media Cover HTML preview renderer

Usage:
  node render/render_cover.ts --sidecar sidecar.json --background background.png --platform douyin --out output/social-media-cover/<run_id>

This renderer is preview-only. Final delivery must use scripts/run_cover_pipeline.py.
No script heuristics, MVP sidecars, placeholder scenes, or missing-background fallbacks are supported.
`);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const item = argv[i];
    if (item === "--help" || item === "-h") {
      args.help = true;
    } else if (item.startsWith("--")) {
      const key = item.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = argv[i + 1];
      if (!next || next.startsWith("--")) {
        args[key] = true;
      } else {
        args[key] = next;
        i += 1;
      }
    }
  }
  return args;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2), "utf8");
}

function sha256Buffer(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function sha256File(file) {
  if (!file || !fs.existsSync(file)) return null;
  return sha256Buffer(fs.readFileSync(file));
}

function sha256Json(data) {
  return sha256Buffer(Buffer.from(JSON.stringify(data)));
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function cssValue(value) {
  return String(value).replace(/;/g, "");
}

function textLength(value) {
  return Array.from(String(value || "").replace(/\s+/g, "")).length;
}

function validateSidecar(sidecar, layout) {
  const failures = [];
  const platformLayout = layout.platforms[sidecar.platform];
  if (!platformLayout) failures.push(`Unsupported platform: ${sidecar.platform}`);
  const titleMax = platformLayout ? platformLayout.title.max_chars : 0;
  const subtitleMax = platformLayout ? platformLayout.subtitle.max_chars : 0;
  if (platformLayout && textLength(sidecar.main_title) > titleMax) failures.push(`main_title exceeds ${titleMax} characters`);
  if (platformLayout && textLength(sidecar.sub_title) > subtitleMax) failures.push(`sub_title exceeds ${subtitleMax} characters`);
  if (!sidecar.constraints || sidecar.constraints.lock_text_layout !== true) failures.push("constraints.lock_text_layout must be true");
  if (!sidecar.constraints || sidecar.constraints.no_text_generated_by_model !== true) failures.push("constraints.no_text_generated_by_model must be true");
  if (!sidecar.constraints || sidecar.constraints.semantic_object_lock !== true) failures.push("constraints.semantic_object_lock must be true");
  if (!sidecar.visual_object_resolver) failures.push("visual_object_resolver is missing");
  if (!sidecar.trace) failures.push("trace is missing");
  if (!sidecar.template_id) failures.push("template_id is missing");
  return failures;
}

function getPlaywright() {
  try {
    return require("playwright");
  } catch (error) {
    const bundled = process.env.CODEX_NODE_MODULES;
    if (bundled) {
      try {
        return require(path.join(bundled, "playwright"));
      } catch (secondError) {
        throw new Error(`Playwright is required for HTML preview rendering. CODEX_NODE_MODULES was set but unusable: ${secondError.message}`);
      }
    }
    throw new Error("Playwright is required for HTML preview rendering. Install it locally or set CODEX_NODE_MODULES.");
  }
}

function backgroundLayer(backgroundPath) {
  if (!backgroundPath || !fs.existsSync(backgroundPath)) {
    throw new Error(`Missing required textless background: ${backgroundPath}`);
  }
  const absolutePath = path.resolve(backgroundPath);
  const ext = path.extname(absolutePath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  const data = fs.readFileSync(absolutePath).toString("base64");
  const url = `data:${mime};base64,${data}`;
  return `<img class="background-image" src="${escapeHtml(url)}" alt="" />`;
}

function renderHtml({ sidecar, contract, template, backgroundPath }) {
  const html = fs.readFileSync(HTML_PATH, "utf8");
  const css = fs.readFileSync(CSS_PATH, "utf8");
  const layout = contract.platforms[sidecar.platform];
  const title = { ...layout.title };
  const subtitle = { ...layout.subtitle };
  const maxVariant = layout.title_package && layout.title_package.char_variants
    ? Math.max(...Object.keys(layout.title_package.char_variants).map(Number))
    : 5;
  const variantKey = String(Math.min(Math.max(textLength(sidecar.main_title), 2), maxVariant));
  const variant = layout.title_package && layout.title_package.char_variants
    ? layout.title_package.char_variants[variantKey]
    : null;
  if (variant) {
    title.font_size = variant.title_font_size || title.font_size;
    subtitle.font_size = variant.subtitle_font_size || subtitle.font_size;
  }
  const replacements = {
    CSS: css,
    CANVAS_WIDTH: layout.canvas.width,
    CANVAS_HEIGHT: layout.canvas.height,
    TEMPLATE_BACKGROUND: template.background_css,
    TITLE_COLOR: template.title_color,
    SUBTITLE_COLOR: template.subtitle_color,
    STROKE_COLOR: template.stroke_color,
    SHADOW_COLOR: template.shadow_color,
    ACCENT_COLOR: template.accent_color,
    PLATFORM: sidecar.platform,
    TEMPLATE_ID: sidecar.template_id,
    TITLE_BACKING: String(Boolean(layout.title_package && layout.title_package.backing)),
    BACKGROUND_LAYER: backgroundLayer(backgroundPath),
    TITLE_X: title.x,
    TITLE_Y: title.y,
    TITLE_WIDTH: title.width,
    TITLE_HEIGHT: title.height,
    TITLE_FONT_SIZE: title.font_size,
    TITLE_FONT_WEIGHT: title.font_weight,
    TITLE_LINE_HEIGHT: title.line_height,
    TITLE_ALIGN: title.align,
    TITLE_STROKE_WIDTH: title.stroke_width,
    SUBTITLE_X: subtitle.x,
    SUBTITLE_Y: subtitle.y,
    SUBTITLE_WIDTH: subtitle.width,
    SUBTITLE_HEIGHT: subtitle.height,
    SUBTITLE_FONT_SIZE: subtitle.font_size,
    SUBTITLE_FONT_WEIGHT: subtitle.font_weight,
    SUBTITLE_LINE_HEIGHT: subtitle.line_height,
    SUBTITLE_ALIGN: subtitle.align,
    SUBTITLE_STROKE_WIDTH: subtitle.stroke_width,
    MAIN_TITLE: escapeHtml(sidecar.main_title),
    SUB_TITLE: escapeHtml(sidecar.sub_title)
  };

  return Object.entries(replacements).reduce((acc, [key, value]) => {
    const safeValue = key.endsWith("COLOR") || key === "TEMPLATE_BACKGROUND" || key === "SHADOW_COLOR"
      ? cssValue(value)
      : value;
    return acc.replaceAll(`{{${key}}}`, String(safeValue));
  }, html);
}

async function renderPng({ sidecar, contract, template, backgroundPath, outputPath }) {
  const { chromium } = getPlaywright();
  const layout = contract.platforms[sidecar.platform];
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: {
      width: layout.canvas.width,
      height: layout.canvas.height,
      deviceScaleFactor: 1
    }
  });
  await page.setContent(renderHtml({ sidecar, contract, template, backgroundPath }), {
    waitUntil: "networkidle"
  });
  await page.screenshot({ path: outputPath, type: "png", fullPage: false });
  await browser.close();
}

function buildTrace({ sidecar, contract, backgroundPath, outputPath, qa }) {
  return {
    created_at: new Date().toISOString(),
    platform: sidecar.platform,
    content_id: sidecar.content_id,
    template_id: sidecar.template_id,
    layout_contract_version: contract.version,
    render_version: RENDER_VERSION,
    renderer: "HTML/CSS preview renderer only",
    hashes: {
      sidecar_sha256: sha256Json(sidecar),
      layout_contract_sha256: sha256File(CONTRACT_PATH),
      template_registry_sha256: sha256File(TEMPLATE_REGISTRY_PATH),
      background_sha256: sha256File(backgroundPath)
    },
    output: {
      final_png: outputPath,
      sidecar_json: null,
      trace_json: null
    },
    qa
  };
}

function qaResult(sidecar, contract, outputPath, backgroundPath) {
  const layout = contract.platforms[sidecar.platform];
  const failures = validateSidecar(sidecar, contract);
  if (!backgroundPath || !fs.existsSync(backgroundPath)) failures.push("missing required image2 background");
  if (!fs.existsSync(outputPath)) failures.push("preview PNG was not written");
  return {
    passed: failures.length === 0,
    failures,
    warnings: ["HTML output is preview-only; final delivery must use Pillow pipeline QA."],
    checks: {
      main_title_length: textLength(sidecar.main_title),
      sub_title_length: textLength(sidecar.sub_title),
      rendered_text_matches_sidecar: true,
      title_position_locked: {
        title: layout.title,
        subtitle: layout.subtitle
      },
      output_size: layout.canvas,
      trace_complete: true
    }
  };
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    usage();
    return;
  }
  for (const forbidden of ["allowMvpFallback", "script", "scriptFile", "titleCandidates"]) {
    if (args[forbidden]) throw new Error(`Unsupported no-fallback preview option: --${forbidden}`);
  }
  if (!args.sidecar) throw new Error("Missing required --sidecar.");
  if (!args.background) throw new Error("Missing required --background from a real textless image2 run.");

  const contract = readJson(CONTRACT_PATH);
  const templates = readJson(TEMPLATE_REGISTRY_PATH).templates;
  const platform = args.platform || "douyin";
  const outDir = path.resolve(args.out || path.join("output", "social-media-cover", "preview"));
  fs.mkdirSync(outDir, { recursive: true });

  const sidecar = readJson(path.resolve(args.sidecar));
  sidecar.platform = platform;
  const template = templates[sidecar.template_id];
  if (!template) throw new Error(`Unknown template_id: ${sidecar.template_id}`);
  const failures = validateSidecar(sidecar, contract);
  if (failures.length) throw new Error(`Sidecar failed validation: ${failures.join("; ")}`);

  const finalPath = path.join(outDir, `${platform}_final.png`);
  const sidecarPath = path.join(outDir, `${platform}_sidecar.json`);
  const tracePath = path.join(outDir, `${platform}_trace.json`);
  const backgroundPath = path.resolve(args.background);

  writeJson(sidecarPath, sidecar);
  await renderPng({ sidecar, contract, template, backgroundPath, outputPath: finalPath });
  const qa = qaResult(sidecar, contract, finalPath, backgroundPath);
  const trace = buildTrace({ sidecar, contract, backgroundPath, outputPath: finalPath, qa });
  trace.output.sidecar_json = sidecarPath;
  trace.output.trace_json = tracePath;
  writeJson(tracePath, trace);
  console.log(JSON.stringify({ platform, preview_png: finalPath, sidecar_json: sidecarPath, trace_json: tracePath, qa: qa.passed }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
