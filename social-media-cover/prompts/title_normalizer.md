# Title Normalizer Prompt

Normalize cover title candidates for a locked layout.

## Input

- Script summary
- User title candidates
- Draft main/subtitle pairs
- Platform

## Output

Return JSON:

```json
{
  "selected": {
    "main_title": "",
    "sub_title": "",
    "reason": ""
  },
  "alternates": [
    { "main_title": "", "sub_title": "", "score": 0, "reason": "" }
  ],
  "qa": {
    "main_title_chars": 0,
    "sub_title_chars": 0,
    "rewrite_required": false
  }
}
```

## Rules

- Default Douyin `account_explainer` mode: main title hard max 8 Chinese characters; subtitle hard max 12 Chinese characters.
- Default WeChat `wechat_editorial_explainer` mode: main title hard max 10 Chinese characters; subtitle hard max 16 Chinese characters.
- Optional `compact_punch` mode: main title hard max 5 Chinese characters; subtitle hard max 8 Chinese characters.
- One line only.
- Do not solve overflow with smaller font, wrapping, punctuation tricks, or spacing tricks.
- Prefer account-style event hooks over generic slogan compression.
- Main title should usually preserve the subject and event: brand/product/person + action/trend/time node.
- Subtitle should usually create a watch reason: implication, question, winner/loser, next step, personal perspective, or hidden method.
- Avoid repeating the same word in main title and subtitle unless it is the product name.
- If both Douyin/Xiaohongshu and WeChat are requested, normalize them independently. WeChat should usually be more complete and editorial than Douyin, not a copy or truncation.
- Reject WeChat pairs that are so short they leave the left title zone visually empty unless the user explicitly wants a sparse magazine cover.

## Candidate Types

Generate and score four options:

- `recommended_account`: closest to the user's account voice.
- `traffic_stronger`: more provocative but still accurate.
- `owner_or_user_angle`: user/community concern.
- `industry_angle`: broader industry interpretation.

Use `title_extraction_rules.md` for scoring and strategy types.
