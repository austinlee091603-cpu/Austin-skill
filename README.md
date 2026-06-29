# Austin Skills

这是一个 Codex Skills 合集仓库。根目录下每一个文件夹都是一个独立 skill，可以单独复制到 `~/.codex/skills/` 使用。

当前包含：

- `social-media-cover`：根据脚本/文章生成抖音/小红书 3:4 竖版、抖音/小红书 4:3 横版和公众号 21:9 封面。默认说“抖音/小红书封面”时，会把 3:4 和 4:3 捆绑输出；也可指定单独渠道。使用流程：使用固定个人头像或虚拟形象作为固定IP，第一次需要先上传，后续默认以这个为准，除非主动上传新的图片。skill默认调用image2模型先生成无文字底图，然后根据脚本/文章提取合适的主副标题，Pillow 最终渲染文字输出成片，确保文字颜色、位置和渠道规则一致。最后会执行 QA 校对。

注：本skill只适用于Codex。

[English](README.en.md)

## 安装方式

安装单个 skill：

```bash
mkdir -p ~/.codex/skills
cp -R social-media-cover ~/.codex/skills/social-media-cover
```

如果你 clone 了整个仓库，也可以从仓库根目录执行：

```bash
mkdir -p ~/.codex/skills
cp -R ./social-media-cover ~/.codex/skills/social-media-cover
```

公开版 skill 不会包含私有头像、私有字体或历史生成结果。使用前请阅读对应 skill 目录里的 `README.md`，按要求补齐本地资产。

## 如何激活

在 Codex 对话里直接点名 skill：

```text
使用 $social-media-cover，根据下面脚本输出抖音/小红书封面和公众号 21:9 封面。默认抖音/小红书会同时输出 3:4 竖版和 4:3 横版，也可以单独指定某个比例或单独公众号封面。
```

如果你的 Codex 使用英文 skill 名触发，也可以说：

```text
Use $social-media-cover to generate covers from this script.
```

## 适合做什么

- 把重复内容生产流程固化成可复用 Codex skill。
- 给自媒体、公众号、短视频账号生产稳定风格的封面。
- 让 AI 负责理解内容和生成底图，让规则负责版式、字体、颜色、QA 和可复现性。
- 需要长期维护个人 IP 形象一致性的内容账号。

## 不适合做什么

- 不想配置本地资产、只想即开即用的模板库。
- 希望每次完全随机出图的灵感探索。
- 让图片模型直接生成最终中文标题的封面。
- 需要绕过 QA、缺图也能交付的占位图流程。

## 仓库结构

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

## 开源说明

仓库只包含 skill 规则、脚本、模板、示例和占位资产说明。头像图、商业字体、生成结果和个人路径不应提交到公开仓库。
