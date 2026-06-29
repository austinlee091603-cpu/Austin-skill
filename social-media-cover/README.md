# Social Media Cover Skill

这个 skill 用于把脚本或文章稳定转成短视频和公众号封面。它的核心不是让模型临场发挥，而是把封面生产拆成可复用流程：

1. 读取全文脚本/文章，提取主题、痛点、冲突、内容类型和标题策略。
2. 锁定个人头像 IP，根据内容规划人物动作、表情、道具和场景互动。
3. 用 image2 生成不带文字的真实底图。
4. 用 Pillow/Freetype 按固定规则渲染主标题和副标题。
5. 输出最终 PNG、sidecar、trace、manifest、QA 报告和 pipeline 报告。

## 安装

把本目录复制到你的 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R social-media-cover ~/.codex/skills/social-media-cover
```

公开版不会自带你的私人头像和字体。首次使用前，请准备：

- `assets/avatar/reference-avatar.png`：你的个人形象锁定图，可以是真人照、虚拟形象、多视角角色表或 3D 卡通形象。
- `assets/fonts/title-font.ttf`：用于标题渲染的中文字体文件。

如果你想使用其他路径，可以改 `config/global_defaults.json` 和 `avatar_bible.json`。缺少头像或字体时，pipeline 会直接失败，不会自动 fallback。

## 激活

在 Codex 对话中可以这样说：

```text
使用 $social-media-cover，根据下面脚本输出抖音/小红书封面和公众号 21:9 封面。
```

也可以只指定一个渠道：

```text
使用 $social-media-cover，输出公众号封面。
```

## 适合做什么

- 抖音/小红书 3:4 竖版封面。
- 抖音/小红书 4:3 横版封面，默认和 3:4 竖版捆绑输出。
- 公众号 21:9 横封面。
- 有固定个人 IP 形象的账号封面。
- 根据完整脚本或文章自动提炼主副标题。
- 希望长期保持封面版式、标题颜色、字体和头像一致的内容账号。

## 不适合做什么

- 没有头像参考图还想直接生成最终封面。
- 没有 image2 底图，只想用占位模板快速凑图。
- 需要模型直接在图片里生成中文标题。
- 需要每次完全随机风格、随机人物、随机版式的视觉探索。

## 使用流程

1. 给 Codex 一份完整脚本或文章。
2. 指定输出渠道：`douyin`、`douyin_xhs_landscape`、`wechat` 或组合输出。只说“抖音/小红书封面”时，默认同时输出 `douyin` 和 `douyin_xhs_landscape`。
3. Codex 根据规则生成平台独立的 sidecar 和 image2 底图。
4. 运行 `scripts/run_cover_pipeline.py` 生成最终图片并跑 QA。
5. 检查 `pipeline_report.json` 中 `passed: true` 后交付。

最终产物默认写入：

```text
./output/social-media-cover/<run_id>/
```

每个平台会包含：

- `{platform}_background.png`
- `{platform}_final_pillow.png`
- `{platform}_sidecar_pillow.json`
- `{platform}_trace_pillow.json`
- `{platform}_qa_report.json`
- `run_manifest.lock.json`
- `pipeline_report.json`

## 设计原则

- AI 负责理解内容、规划视觉和生成底图。
- 规则负责标题长度、布局、颜色、字体、头像锁定和 QA。
- 人负责最后判断底图是否真正表达了脚本。
- 没有 fallback。资产缺失、底图失败、QA 失败，都应该停下来修正，而不是生成占位图。
