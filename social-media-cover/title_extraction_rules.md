# Title Extraction Rules

The cover title is not a transcript summary. It is an account-style entry point: anchor the event, then create a reason to watch.

## Default Title Mode

Use `account_explainer` by default for Douyin/Xiaohongshu covers.

- Main title: `4-8` Chinese characters, hard max `8`.
- Subtitle: `4-12` Chinese characters, hard max `12`.
- Both are one line only.
- Do not resize, wrap, condense, or move text to fit. Select a locked font-size variant from `layout_contract.json`; if still too long, rewrite.

Use `landscape_account_explainer` by default for Douyin/Xiaohongshu 4:3 landscape covers.

- Main title: `5-10` Chinese characters, hard max `10`.
- Subtitle: `5-15` Chinese characters, hard max `15`.
- Both are one line only.
- The 4:3 canvas has about 25% more title capacity than 3:4, but it is still a short-video cover, not a WeChat editorial cover. Keep the same centered top title principle, punchy account voice, and similar large-font impact as the vertical cover.
- Do not simply crop or reuse the vertical text placement. Generate a platform-specific title pair when the horizontal layout benefits from a slightly more complete viewing reason.

Use `wechat_editorial_explainer` by default for WeChat 21:9 covers.

- Main title: `6-10` Chinese characters, hard max `10`.
- Subtitle: `8-16` Chinese characters, hard max `16`.
- Both are one line only.
- WeChat should normally be more explanatory than Douyin because the horizontal canvas has a wider left title field. Do not simply copy the Douyin title pair unless it is already the strongest WeChat title.
- Prefer a more complete editorial entry point: `事件/资源/方法 + outcome` in main title, and `benefit/use case/viewing reason` in subtitle.

Use `compact_punch` only when the user asks for ultra-short poster words or the script is naturally label-like.

- Main title: `3-5` Chinese characters.
- Subtitle: `5-8` Chinese characters.

## Account Voice

For this account, prefer:

- Industry event + explanation rights.
- Clear subject, clear event, restrained but clickable wording.
- Questions that ask what the event means, who benefits, who pays, what changes, or what comes next.
- Insider/participant perspective when present in the script.
- Avoid empty shock words, vague slogans, and title-only conclusions that remove curiosity.

Good account-style examples:

- `极越正式重组` / `意味着什么？`
- `极越一周年后` / `车主为什么依旧热爱？`
- `极越新车将面世？` / `首席设计师猛爆料`
- `Openclaw爆火` / `我对智能汽车的思考`
- `英伟达智驾开源` / `BBA们要躺赢？`
- `吉利重组马丁案` / `极越的救星是谁？`
- Douyin workflow example: `封面Skill` / `我把它开源了`
- WeChat workflow example: `封面Skill开源` / `脚本到成片工作流`

## Title Strategy Types

Classify each script before writing titles. Use the type to choose title grammar.

1. **Event explainer**
   - Main: subject + event.
   - Subtitle: `意味着什么？` / `影响有多大？` / `下一步看什么？`
   - Example: `极越正式重组` / `意味着什么？`

2. **Owner/community sentiment**
   - Main: brand or community time node.
   - Subtitle: why-love, why-wait, why-stay question.
   - Example: `极越一周年后` / `车主为什么依旧热爱？`

3. **Leak/prediction**
   - Main: upcoming event with question mark.
   - Subtitle: source or information edge.
   - Example: `极越新车将面世？` / `首席设计师猛爆料`

4. **Tool or product outbreak**
   - Main: product/tool + outbreak/new opportunity.
   - Subtitle: creator's interpretation or use case.
   - Example: `Openclaw爆火` / `我对智能汽车的思考`

5. **Open-source/industry leverage**
   - Main: company + technology + open-source/action.
   - Subtitle: who wins, who can coast, who is disrupted.
   - Example: `英伟达智驾开源` / `BBA们要躺赢？`

6. **Rescue/capital/restructure case**
   - Main: company + restructure/case.
   - Subtitle: who is the rescuer or what it implies.
   - Example: `吉利重组马丁案` / `极越的救星是谁？`

7. **Learning/resource recommendation**
   - Main: time + action field.
   - Subtitle: exact number or target list.
   - Example: `2026年学AI` / `认准这8位博主`

8. **Full interpretation/deep dive**
   - Main: trend/opportunity.
   - Subtitle: full解读, 全量解读, 一次说清.
   - Example: `AI新机遇` / `codex全量解读`

9. **Workflow/build story**
   - Douyin main: surprising outcome, tool/resource, or release event within 8 chars.
   - Douyin subtitle: how-I-built/process hook or open-source/use-case reason within 12 chars.
- Douyin/Xiaohongshu landscape main: same hook grammar within 10 chars, rendered in the same centered top short-video title system as vertical.
- Douyin/Xiaohongshu landscape subtitle: process/use-case reason within 15 chars, centered under the main title.
   - WeChat main: resource/method + release/outcome within 10 chars.
   - WeChat subtitle: workflow value, platform coverage, or creator benefit within 16 chars.
   - Example: `AI替我熬夜` / `我是如何搭建Agent的`
   - Example: `封面Skill` / `我把它开源了`
   - WeChat example: `封面Skill开源` / `脚本到成片工作流`

10. **Evaluation/comparison**
    - Main: category + test.
    - Subtitle: winner question.
    - Example: `文生图AI测评` / `谁是性价比之王`

11. **Hidden use / private assistant**
    - Main: product + hidden usage.
    - Subtitle: personal assistant or private workflow question.
    - Example: `豆包隐藏用法` / `我的私人助理？`

12. **Counter-consensus**
    - Main: accepted hot trend.
    - Subtitle: restrained reversal.
    - Example: `AI大爆发` / `并没有开始普及`

## Candidate Generation

Always generate at least four title pairs:

- `recommended_account`: best match to this account's voice.
- `traffic_stronger`: more provocative but still accurate.
- `owner_or_user_angle`: user/community concern when applicable.
- `industry_angle`: broader market or technology interpretation.

When both Douyin/Xiaohongshu ratios and WeChat are requested, generate and score separate candidate sets for each platform. The 4:3 landscape set may reuse the 3:4 wording only if it remains the strongest option; otherwise it should use the extra horizontal space for a slightly more complete hook while keeping the same centered top short-video hierarchy. The WeChat set must not be a mechanical truncation of the Douyin set.

For each pair, record:

- `strategy_type`
- `main_title`
- `sub_title`
- `why_it_works`
- `risk`
- `score`

## Scoring

Score from 0 to 100:

- Subject/event specificity: 20
- Curiosity or question value: 20
- Account voice fit: 20
- Accuracy and non-misleading wording: 15
- Visual readability and length fit: 15
- Freshness/traffic energy: 10

Reject if:

- Main title loses the core subject when the script is about a named company/product/person.
- Subtitle merely repeats the main title.
- The pair sounds like a generic slogan.
- The title gives away the whole answer and removes curiosity.
- The wording is legally or factually stronger than the script supports.
- WeChat title pair is unnecessarily short and leaves the 21:9 title zone feeling empty.
- Douyin title pair is too editorial and loses first-glance impact.
- Douyin/Xiaohongshu 4:3 landscape title pair wastes the extra horizontal title space without improving clarity, becomes so long that it loses short-video cover impact, or encourages a WeChat-like left-title/right-visual layout.
- WeChat title pair fits character count but would exceed the left 50% rendered text boundary at the locked font size.

## Rewrite Order

If too long:

1. Keep subject and event first.
2. Remove weak adjectives.
3. Replace full sentence with event phrase or question phrase.
4. Move details from main title to subtitle.
5. If still too long, choose a different title strategy rather than shrinking font.
