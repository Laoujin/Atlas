---
title: "Live Regression Demo Design"
date: 2026-06-09
depth: standard
format: md
topic: "Live regression demo design"
topic_raw: "Live regression demo design"
issue: 206
tags: [evals, live-demo, promptfoo, regression-testing, conference-talk, llm, demo-design]
summary: "How to design a 3-minute live regression demo that converts skeptics: the right scenario, promptfoo as the demo tool, cached responses for reliability, and scripted keypresses via Demo Time."
citations: 15
reading_time_min: 5
model: "Sonnet 4.6"
cost_usd: "sub"
cost_usd: 1.42
duration_sec: 538
model: "Sonnet 4.6"
cover: cover.svg
---

> **Decision** Use [promptfoo](https://www.promptfoo.dev) ⭐ 22k [[4]](https://github.com/promptfoo/promptfoo) with `--cache` enabled. One scenario: a support-agent prompt edit that silently collapses refusal behavior — invisible to eyeballing, visible in the eval table. Three acts: manual "looks good" → quiet prompt edit → eval catches it. Record a 60-second fallback video before you go on stage. [[8]](https://dev.to/measuredco/how-to-do-great-live-demos-and-why-theyre-important-to-get-right-24lc)

## The right scenario

The demo has one job: show that eyeballing a single response doesn't catch what evals catch across the suite. Pick a scenario where the regression is **invisible per-response but visible as a pattern**. [[14]](https://www.vitorsousa.com/blog/beyond-the-vibe-check-a-systematic-approach-to-llm-evaluation/)

The canonical example from the FutureAGI regression playbook [[1]](https://futureagi.com/blog/prompt-regression-testing-2026/): a support agent that handles refund requests. You add one line to the system prompt — `"Always respond in a warm, conversational tone"` — and every individual response looks friendlier. But across a 15-case golden set, refusal rate on legitimate refund requests climbs 14 points. [[2]](https://futureagi.com/glossary/llm-regression-testing/) Overall metrics may even improve (e.g. 0.91→0.93) while a specific cohort collapses (0.94→0.83). The eval catches this in 90 seconds; manual review never would.

This works because it passes the **"I would have done that" test** — every developer in the room has shipped a well-intentioned wording change that silently altered behavior elsewhere. The non-determinism and prompt sensitivity that make LLM regression testing hard [[3]](https://arxiv.org/abs/2311.11123) are exactly what makes the demo convincing.

**Prepare two artefacts:**

- `v1-prompt.txt` — original system prompt
- `v2-warm-tone.txt` — one line added: `"Always respond in a warm, conversational tone."`
- `promptfooconfig.yaml` — 12–15 test cases: ~60% happy-path refunds, ~25% legitimate refund requests, ~15% edge-case phrasing [[1]](https://futureagi.com/blog/prompt-regression-testing-2026/)
- Assertions: `llm-rubric` for tone quality; `icontains` for refusal detection

Keep the test suite at 12–15 cases (not the full golden set). Demo time is budget, not coverage.

## The 3-act arc

**Act 1 — The vibe check (30 sec)**
Show a terminal: `curl` the agent with a refund request. Response comes back. "Looks good, ship it." Slide title: *"This is how most teams test today."* The audience recognises it. [[14]](https://www.vitorsousa.com/blog/beyond-the-vibe-check-a-systematic-approach-to-llm-evaluation/)

**Act 2 — The innocent edit (20 sec)**
Show `git diff v1-prompt.txt v2-warm-tone.txt`. One line added. Ask the room: *"Would you approve this PR?"* Most nods. [[1]](https://futureagi.com/blog/prompt-regression-testing-2026/)

**Act 3 — The eval catches it (2 min)**
Run `promptfoo eval --config promptfooconfig.yaml`. The pass/fail table populates live in terminal. Red cells appear on the refund-rejection cases. Run `promptfoo view` — the browser opens a scatter plot where v2 pulls left (lower score) on the refusal rubric. [[5]](https://www.promptfoo.dev/docs/usage/web-ui/) [[6]](https://www.datacamp.com/tutorial/promptfoo-tutorial)

The punchline, said aloud: *"The single-response curl looked fine. Fourteen cases disagreed."* That's the talk's thesis, demonstrated.

## Tool: promptfoo for demo work

[promptfoo](https://www.promptfoo.dev) ⭐ 22k [[4]](https://github.com/promptfoo/promptfoo) wins for live demo use over DeepEval and Langfuse for three concrete reasons [[15]](https://medium.com/@srinib100/llm-evaluation-frameworks-deepeval-promptfoo-and-giskard-ad4e1547ec1c):

| Reason             | Detail                                                                           |
|--------------------|----------------------------------------------------------------------------------|
| Terminal output    | Pass/fail table prints live as tests run — audience sees it building in real-time |
| YAML config        | `promptfooconfig.yaml` is readable when projected; pytest files are not           |
| Web viewer         | `promptfoo view` opens browser table + scatter plot in one command [[5]](https://www.promptfoo.dev/docs/usage/web-ui/) |

The [promptfoo-demo-evals](https://github.com/adelmuursepp/promptfoo-demo-evals) ⭐ 0 repo [[7]](https://github.com/adelmuursepp/promptfoo-demo-evals) provides a language-learning guided use case — useful as a structural reference even if you don't run it verbatim.

DeepEval is better if your team is Python-native and wants `assert` statements in pytest. But projecting pytest output live is awkward; the failure messages are verbose and test IDs are opaque to an audience unfamiliar with the codebase. [[15]](https://medium.com/@srinib100/llm-evaluation-frameworks-deepeval-promptfoo-and-giskard-ad4e1547ec1c)

## Keeping the demo safe

**Do not rely on temperature=0.** It governs only the token-selection rule, not floating-point inference on parallel hardware. Two calls to the same model with the same prompt can diverge even at temp=0, especially across Mixture-of-Experts routing. [[12]](https://www.zansara.dev/posts/2026-03-24-temp-0-llm/)

Use a layered safety strategy instead:

1. **Cache first** — `promptfoo eval --cache` stores responses keyed to (prompt + model + params). First run hits the API; every subsequent run (rehearsal, live stage) is instant and identical. [[13]](https://medium.com/@2nick2patel2/llm-determinism-in-prod-temperature-seeds-and-replayable-results-8f3797583eb1)
2. **Local model fallback** — wire the config to Ollama for fully offline determinism. Smaller model = weaker rubric quality, but demo consistency beats live variance. [[4]](https://github.com/promptfoo/promptfoo)
3. **Pre-recorded backup** — record a 60-second terminal capture of the demo working. Load it in a video player on a hidden virtual desktop. Switch to it silently if the live run hangs or the API rate-limits on conference Wi-Fi. [[8]](https://dev.to/measuredco/how-to-do-great-live-demos-and-why-theyre-important-to-get-right-24lc)

**API key hygiene:** Set `OPENAI_API_KEY` in your shell session before the talk, not inline in the config. Keep a spare key in a `.env` file. Conference Wi-Fi sometimes rate-limits unfamiliar source IPs.

## Presentation mechanics

**[Demo Time](https://demotime.show/)** [[9]](https://demotime.show/) is a VS Code extension that scripts every step as a keypress — pre-define each file edit, terminal command, and highlight; execute with a single key. No typos, no forgotten flags, no context switch between slides and terminal. [[10]](https://dev.to/estruyf/making-live-coding-demos-easier-with-demo-time-d8o) Used at Microsoft Ignite and OpenAI DevDay. [[11]](https://gitnation.com/contents/improve-your-presentation-skills-by-scripting-your-live-coding-demos-to-perfection)

Configure the environment before going on stage:

- Light theme (dark terminals wash out on conference projectors)
- Terminal font size 28–32pt
- Block cursor (thin blinking cursors disappear at distance)
- Hide tabs, file tree, status bar
- Close all other terminal windows and browser tabs

Rehearse the full demo at least 10 times. Run it once on a clean machine with a fresh shell. Run it once with Wi-Fi disabled to confirm the cache path works. [[8]](https://dev.to/measuredco/how-to-do-great-live-demos-and-why-theyre-important-to-get-right-24lc)

## Time budget

| Segment              | Time      | Notes                                          |
|----------------------|-----------|------------------------------------------------|
| Act 1: vibe check    | 30 sec    | Single curl, "looks fine"                      |
| Act 2: the edit      | 20 sec    | `git diff`, one-line change                    |
| Act 3: eval runs     | 90 sec    | Table populates, `promptfoo view` opens        |
| Commentary/pause     | 40 sec    | "One rubric. Fourteen cases. Ship it?"         |
| **Total**            | **~3 min**| Target for a 30-min talk                       |

Over-rehearse so you can cut Act 1 if you're running long. Never cut Act 3 — the pass/fail table **is** the talk's evidence.
