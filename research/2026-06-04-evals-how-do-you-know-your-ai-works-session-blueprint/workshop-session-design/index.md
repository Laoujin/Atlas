---
title: "Teaching Evals: A 2h Hands-On Workshop (and Talk Variant) for Expert Devs"
date: 2026-06-04
depth: standard
format: md
model: "Opus 4.8"
duration_sec: 210
cost_usd: "sub"
topic: "Design a 2-hour hands-on workshop (and talk-only variant) teaching LLM/AI evals to expert developers: a runnable lab arc (golden dataset → LLM-as-judge grader → CI regression gate → catch a planted regression live), which eval framework to standardize on and why, datasets/fixtures, prereqs/setup, minute-by-minute timing, best live demos and aha moments, and workshop-vs-talk tradeoffs, drawing on how practitioners teach evals in 2026"
topic_raw: "Design a 2-hour hands-on workshop (and a talk-only variant) that teaches LLM/AI evals to expert developers — a concrete runnable lab arc, which eval framework to standardize the lab on and why, datasets/fixtures to ship to attendees, prerequisites and setup, a minute-by-minute timing breakdown, the best live demos and aha moments, and the tradeoffs between running this as a hands-on workshop vs a talk. Draw on how practitioners and courses actually teach evals in 2026"
tags: [evals, llm, workshop, teaching, deepeval, ci, llm-as-judge]
summary: "A runnable 2h evals lab on DeepEval — golden set → LLM-judge → CI gate → planted regression — with timing, fixtures, and the workshop-vs-talk call."
citations: 19
reading_time_min: 9
cover: cover.svg
---

> **Decision.** Build the workshop as a **runnable lab arc on [DeepEval](https://deepeval.com)** ⭐ 16k [[4]](https://deepeval.com/docs/getting-started) — Python-native, pytest-based, CI-ready — *not* on Promptfoo, which OpenAI acquired in March 2026 and which is now a strategic risk for a vendor-neutral teaching lab [[6]](https://x.com/OpenAI/status/2031052793835106753)[[7]](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/). Teach evals the way Hamel Husain & Shreya Shankar do: **error analysis first, judge second, gate third** [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/). The single best "aha" is the **planted-regression reveal**: a green CI pipeline turns red on a one-line prompt edit the eye would miss. **Run it hands-on if seats ≤ 30 and you can pre-ship a devcontainer; run the talk variant otherwise** — laptop/setup chaos is the dominant failure mode of live labs [[13]](https://www.eventible.com/learning/conference-vs-seminar-vs-workshop/).

## Why DeepEval for the lab (and not Promptfoo)

The 2026 framework field narrowed to two leaders, then forked on ownership.

| Axis                  | DeepEval ⭐ 16k                          | Promptfoo ⭐ 22k                           | Phoenix ⭐ 10k                  |
|-----------------------|------------------------------------------|--------------------------------------------|--------------------------------|
| Model                 | Python + pytest test cases [[4]][a]      | Declarative YAML assertions [[8]][b]       | OTel tracing + evals [[16]][c] |
| LLM-as-judge          | `GEval`, 50+ metrics [[3]][d]            | Built-in + custom graders [[8]][b]         | Pre-built evaluators [[16]][c] |
| CI gate               | `deepeval test run` → non-zero exit [[5]][e] | CLI + CI/CD configs [[8]][b]           | Via test harness [[16]][c]     |
| Golden dataset        | `Golden`/`EvaluationDataset` [[12]][f]   | YAML test rows [[8]][b]                     | Dataset objects [[16]][c]      |
| 2026 ownership risk   | Independent (Confident AI)               | ⚠ Owned by OpenAI since Mar 2026 [[7]][g]  | Independent (Arize)            |
| Teaching fit          | ✓ Devs already know pytest               | ✓ Lowest setup, but config-not-code         | Heavier; tracing-first         |

[a]: https://deepeval.com/docs/getting-started
[b]: https://github.com/promptfoo/promptfoo
[c]: https://github.com/Arize-ai/phoenix
[d]: https://dev.to/thedailyagent/top-5-ai-agent-eval-tools-after-promptfoos-exit-576i
[e]: https://deepeval.com/guides/guides-regression-testing-in-cicd
[f]: https://deepeval.com/docs/evaluation-datasets
[g]: https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/

For an audience of **expert software consultants**, DeepEval's pytest model is the right pedagogical lever: they already know `assert`, fixtures, and red/green CI — the lab teaches *eval thinking*, not a new tool's DSL [[4]](https://deepeval.com/docs/getting-started). Promptfoo is genuinely lower-setup (YAML, no Python) [[8]](https://github.com/promptfoo/promptfoo), but two things kill it for this session: (1) **OpenAI now owns it** [[6]](https://x.com/OpenAI/status/2031052793835106753)[[7]](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/) — awkward for a vendor-neutral consultancy teaching client-facing rigor, with open community doubt about long-term provider neutrality [[7]](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/); and (2) YAML assertions hide the judge logic the workshop wants attendees to *write*. Mention Promptfoo as the "I want this in an afternoon, no Python" alternative, and Braintrust/Phoenix as the platform/tracing options [[14]](https://www.braintrust.dev/articles/best-promptfoo-alternatives-2026)[[16]](https://github.com/Arize-ai/phoenix).

## The teaching spine: error-analysis-first

The canonical 2026 method is Hamel Husain & Shreya Shankar's loop [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/)[[2]](https://maven.com/parlance-labs/evals), and the workshop should inherit its order — most teams fail by jumping straight to metrics:

1. **Open coding** — skim 50-100 real traces (~30s each), jot what *actually* broke; no root-causing yet [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
2. **Axial coding** — cluster notes into specific failure categories (e.g. "conversational flow", "tool-call failure"), not vague ones [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
3. **Quantify** — pivot-table the categories to see which failure dominates [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
4. **Build a binary LLM-as-judge** for the top failure mode — true/false, not Likert, because shipping decisions are binary [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/)[[15]](https://www.evidentlyai.com/llm-guide/llm-as-a-judge).
5. **Align the judge to human labels** — measure TPR and TNR *separately*; raw agreement is a trap when failures are rare (a "always-pass" judge scores 90%) [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
6. **Gate it** — the golden set + judge become a regression suite in CI [[5]](https://deepeval.com/guides/guides-regression-testing-in-cicd).

Compress steps 1-3 to a 10-minute taste in a 2h slot (full error analysis is its own hour); the runnable arc is steps 4-6. This mirrors how Evidently [[9]](https://www.evidentlyai.com/llm-evaluations-course) and W&B [[17]](https://wandb.ai/site/courses/evals/) structure their applied tracks: custom judges → datasets → CI/monitoring.

## The lab arc (what attendees build)

Ship a **toy app with seeded failures** — reuse the community-standard "Recipe Bot" shape [[18]](https://arize.com/blog/ai-evals-maven-course-homework-the-recipe-bot-workflow/) or any small RAG/agent. Four checkpoints, each a green tick before moving on:

| # | Build                          | Concept landed                                        | Cite |
|---|--------------------------------|-------------------------------------------------------|------|
| 1 | **Golden dataset** (20-40 rows)| `Golden`→`LLMTestCase`; ground truth from labeled traces | [[12]][h] |
| 2 | **LLM-as-judge grader**        | `GEval` rubric, binary pass/fail, threshold tuning    | [[4]][i] |
| 3 | **Judge alignment check**      | TPR/TNR vs your hand-labels; iterate the rubric       | [[1]][j] |
| 4 | **CI regression gate**         | `deepeval test run` in GitHub Actions, non-zero = red | [[5]][k] |

[h]: https://deepeval.com/docs/evaluation-datasets
[i]: https://deepeval.com/docs/getting-started
[j]: https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/
[k]: https://deepeval.com/guides/guides-regression-testing-in-cicd

**The planted regression (the payoff).** Before the session, prepare a second branch where one prompt line is subtly degraded (e.g. drop "only use the provided context" → judge starts passing hallucinations). Attendees push it; **green CI goes red** automatically because the alignment-tuned judge catches what eyeballing the diff would not [[5]](https://deepeval.com/guides/guides-regression-testing-in-cicd). That red X is the whole session in one moment. For an advanced bonus, show 2026's CI patterns: assert on `pass_rate`/`avg_score`/p50-p95 percentiles and route-tag goldens so a PR diff only re-runs affected routes [[11]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

### Fixtures to ship attendees

- `goldens.csv` / `goldens.json` — 20-40 labeled rows (DeepEval loads either) [[19]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd).
- `traces/` — 60-80 raw output traces for the 10-min error-analysis taste [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
- `app/` — the toy bot, plus a `regression` branch with the planted defect.
- `.github/workflows/evals.yml` — the gate, pre-written; attendees only flip the trigger [[5]](https://deepeval.com/guides/guides-regression-testing-in-cicd).
- Pre-recorded judge/CI run output as a **fallback** if API keys or network die.

## Prerequisites & setup (the part that makes or breaks the live version)

Setup failure is the #1 hands-on-workshop killer [[13]](https://www.eventible.com/learning/conference-vs-seminar-vs-workshop/). Mitigate hard:

- **Ship a devcontainer / Codespace** with `deepeval`, `pytest`, and deps pinned — one click, no local Python roulette [[4]](https://deepeval.com/docs/getting-started).
- **Pre-distribute API keys** (or a shared proxy with a budget cap); never have 30 people make accounts live. Set `DEEPEVAL_RESULTS_FOLDER` for local JSON so nobody *needs* a cloud login [[4]](https://deepeval.com/docs/getting-started).
- **Offline judge option** — point `GEval` at a small local model so a dead network doesn't kill the room.
- **A pre-seeded GitHub repo per attendee** (or a fork button) so the CI step actually runs Actions [[5]](https://deepeval.com/guides/guides-regression-testing-in-cicd).
- Prereq for attendees: comfortable with Python + pytest + git PRs. Skip 101 — they're experts.

## Minute-by-minute (2h hands-on)

| Time      | Segment                              | Mode        |
|-----------|--------------------------------------|-------------|
| 0:00-0:10 | Why evals; the planted-regression promise (cold open the payoff) | talk |
| 0:10-0:20 | Error analysis taste: open→axial on `traces/` | hands-on |
| 0:20-0:25 | Buffer / setup triage                | —           |
| 0:25-0:45 | **CP1** build golden dataset         | hands-on    |
| 0:45-1:10 | **CP2** write the `GEval` judge      | hands-on    |
| 1:10-1:30 | **CP3** align judge: TPR/TNR, iterate rubric | hands-on |
| 1:30-1:35 | Break / buffer                       | —           |
| 1:35-1:55 | **CP4** wire the CI gate; **push the planted regression → red** | hands-on |
| 1:55-2:00 | Debrief: what to do Monday, prod monitoring next step | talk |

Buffers at 0:20 and 1:30 are non-negotiable — labs always run long, and CP2 (judge-writing) is where people stall. If time slips, **cut CP3's depth, never CP4** — the red-CI reveal is the session.

## Live demos & "aha" moments (ranked)

1. **Green→red CI on a one-line prompt edit** — the headline; eyeballing missed it, the judge didn't [[5]](https://deepeval.com/guides/guides-regression-testing-in-cicd).
2. **The "always-pass" judge scoring 90% accuracy** — show the trap metric live, then split into TPR/TNR and watch the judge look terrible [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
3. **Binary vs Likert** — let two attendees grade the same output on 1-5 and disagree, then re-grade binary and converge [[1]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/).
4. **Rubric edit → score flip** — tighten one judge sentence, re-run, watch a borderline case flip; evals are code you debug [[15]](https://www.evidentlyai.com/llm-guide/llm-as-a-judge).
5. **Spot-check the judge** — sample 5-10% of verdicts against human calls to keep it honest [[10]](https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method).

## Workshop vs talk: the tradeoff

A workshop's value is hands-on muscle memory; a talk's is reach and zero setup risk [[13]](https://www.eventible.com/learning/conference-vs-seminar-vs-workshop/).

| Factor              | Hands-on workshop                          | Talk-only variant                          |
|---------------------|--------------------------------------------|--------------------------------------------|
| What sticks         | Muscle memory: they've *built* a gate      | Mental model + a repo to try later         |
| Audience cap        | ≤ ~30 (support per person) [[13]][l]       | Unbounded                                  |
| Failure mode        | ⚠ Setup/laptop/key chaos eats time [[13]][l] | Passive; no "I did it" moment            |
| Prep cost           | High: devcontainer, keys, per-attendee repo | Low: slides + screen-recorded lab          |
| Best when           | Internal team, paid client, small cohort   | Conference keynote, large meetup           |

[l]: https://www.eventible.com/learning/conference-vs-seminar-vs-workshop/

**Talk variant (45-60 min).** Same spine, you drive: cold-open the red CI, then rewind and *narrate* building golden set → judge → alignment → gate using **pre-recorded terminal clips** (live judge calls are slow and flaky on stage). End by handing out the repo so attendees run CP1-4 themselves. This is also your **fallback if the hands-on room melts down** — switch to driving from your machine and keep the payoff intact.

**Hybrid (recommended default for Itenium):** demo-driven talk with **two short "you try it" beats** (write the judge rubric; push the regression). Captures most of the muscle-memory value while bounding setup risk — and degrades gracefully to a pure talk if the room's environments fail.

---

scout: standard depth, single pass. DeepEval star count via GitHub API on 2026-06-04.
