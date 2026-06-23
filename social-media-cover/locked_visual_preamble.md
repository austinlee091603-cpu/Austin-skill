# Locked Visual Preamble

Version: `v1.2.0`

This file is the visual constitution for Social Media Cover. It defines immutable cover rules. Models may read it, but they must not reinterpret or relax it.

## Canvas

- Douyin: `1080x1440`, ratio `3:4`, PNG.
- WeChat official account: `1260x540`, ratio `21:9`, PNG.
- Backgrounds must be high contrast and readable after the compositor adds text.

## Title System

- Main title is always one line.
- Douyin account-title main title must be `<= 8` Chinese characters.
- WeChat editorial main title must be `<= 10` Chinese characters.
- Compact punch main title must be `<= 5` Chinese characters.
- Subtitle is always one line.
- Douyin account-title subtitle must be `<= 12` Chinese characters.
- WeChat editorial subtitle must be `<= 16` Chinese characters.
- Compact punch subtitle must be `<= 8` Chinese characters.
- Title and subtitle coordinates, font size, font weight, stroke, shadow, line height, and alignment are locked by `layout_contract.json`.
- If text is too long, rewrite the text. Do not shrink, wrap, compress, or move it.
- Douyin covers must use a first-glance title package: centered or center-top placement, heavy weight, no compositor stroke, no compositor shadow, and no forced backing by default.
- Title packaging is a coordination between the image2 background and locked compositor layer. Do not leave thin text floating on a busy background; solve readability with a quiet scene-native buffer behind the title.
- Douyin title safety should come from the image2 background: a quiet, low-detail, scene-native buffer behind the title with weak edges and roughly 60-120px visual breathing room. Do not force a visible rectangular title frame in the compositor by default.
- WeChat title safety should come from the image2 background too: the left title area should be readable enough for light/no stroke and light/no shadow.
- Character-count adaptation is allowed only by selecting a predefined locked variant from `layout_contract.json`; never use arbitrary auto-fit.

## Avatar IP

- Default to the user's fixed virtual personal avatar.
- Default locked avatar reference: `assets/avatar/reference-avatar.png` when present, unless the user supplies a new reference or explicitly asks to change identity.
- The avatar is an emotional actor in the cover, not a pasted logo or corner sticker.
- The avatar should participate in the content metaphor: pointing, holding, reacting, guarding, warning, presenting, comparing, or interacting with a prop.
- Do not create random human replacements. Preserve the user's face shape, hair, rendering style, and temperament from the reference image.
- Mutable: expression, action, outfit, prop, interaction object, scene relationship.
- Immutable: face shape, hairstyle, baseline rendering style, overall temperament, long-term brand identity.
- Keep avatar outside the final title text boxes, but allow the avatar to be near the title if the gesture supports the title and does not reduce readability.

## Visual Hierarchy

1. Main title.
2. Subtitle.
3. Avatar action and expression.
4. Props and scene metaphor.
5. Atmosphere and texture.

## Forbidden

- image2 generating final readable Chinese title text.
- Random large Chinese words in the background.
- Avatar covering the title area.
- Font auto-scaling.
- Layout drift between templates.
- One-off styles that conflict with the locked avatar IP.
- Manual cutout-and-paste avatar composites as final backgrounds, unless explicitly marked as a throwaway wireframe.
- Placeholder, flat geometric, stick-figure, or renderer MVP backgrounds as final delivery.
- Abstract decorative blocks that do not explain the script hook.
- Backgrounds that do not look like a real social media cover after text is removed.
